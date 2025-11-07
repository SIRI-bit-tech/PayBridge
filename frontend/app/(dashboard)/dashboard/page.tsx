"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { graphQLQuery } from "@/lib/api"
import { WebSocketClient } from "@/lib/websocket"
import type { Analytics } from "@/types"

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [wsConnected, setWsConnected] = useState(false)

  // Fetch analytics via GraphQL
  useEffect(() => {
    const fetchAnalytics = async () => {
      const query = `
        query {
          analytics {
            totalTransactions
            totalVolume
            successRate
            averageTransactionSize
            transactionsByProvider
            transactionsByStatus
            dailyVolume
          }
        }
      `
      const response = await graphQLQuery<any>(query)
      if (response.data?.analytics) {
        setAnalytics(response.data.analytics)
      }
    }

    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])

  // Real-time WebSocket updates
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
    if (!token) return

    const ws = new WebSocketClient(token)
    ws.connect("/ws/dashboard/")
      .then(() => {
        setWsConnected(true)
        ws.send("subscribe_analytics", {})
      })
      .catch((err) => console.error("[v0] WebSocket connection failed:", err))

    ws.on("analytics", (data: any) => {
      console.log("[v0] Received analytics update:", data)
      setAnalytics((prev) => ({ ...prev, ...data.data }))
    })

    return () => {
      ws.disconnect()
      setWsConnected(false)
    }
  }, [])

  if (!analytics) {
    return <div className="p-8 text-foreground">Loading analytics...</div>
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Real-time payment analytics and insights</p>
        {wsConnected && <p className="text-xs text-secondary mt-2">🟢 Real-time connection active</p>}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{analytics.total_transactions}</div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">₦{Number(analytics.total_volume).toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-secondary">{analytics.success_rate.toFixed(1)}%</div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Transaction</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              ₦{Number(analytics.average_transaction_size).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Volume Chart */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Daily Volume (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={analytics.daily_volume || []}>
                <defs>
                  <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} />
                <Area type="monotone" dataKey="volume" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorVolume)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Transactions by Provider */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Transactions by Provider</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={Object.entries(analytics.transactions_by_provider || {}).map(([provider, data]) => ({
                  provider,
                  count: (data as any).count,
                  volume: (data as any).volume,
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="provider" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} />
                <Legend />
                <Bar dataKey="count" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Status Distribution */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Transactions by Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {Object.entries(analytics.transactions_by_status || {}).map(([status, count]) => (
              <div key={status} className="bg-muted rounded p-4">
                <p className="text-muted-foreground text-sm capitalize">{status}</p>
                <p className="text-2xl font-bold text-primary mt-2">{count}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
