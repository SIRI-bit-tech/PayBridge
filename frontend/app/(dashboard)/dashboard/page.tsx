"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity } from "lucide-react"
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
import { apiCall } from "@/lib/api"
import { useDashboardSocketIO } from "@/lib/useDashboardSocketIO"
import type { Analytics } from "@/types"
import { RecentTransactions } from "@/components/dashboard/RecentTransactions"
import { ActivityFeed } from "@/components/dashboard/ActivityFeed"
import { SettlementSummary } from "@/components/dashboard/SettlementSummary"
import { SystemHealth } from "@/components/dashboard/SystemHealth"
import { UserSummary } from "@/components/dashboard/UserSummary"

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)

  // Fetch analytics via REST API (with GraphQL fallback)
  useEffect(() => {
    const fetchAnalytics = async () => {
      console.log('Fetching analytics...')
      
      // Check if user is logged in
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
      if (!token) {
        console.error('No access token found.')
        // Set empty analytics instead of redirecting
        setAnalytics({
          total_transactions: 0,
          total_volume: 0,
          success_rate: 0,
          average_transaction_size: 0,
          transactions_by_provider: {},
          transactions_by_status: {},
          daily_volume: []
        })
        return
      }
      
      console.log('Token found, fetching data...')
      
      // Try REST API first (more reliable)
      const restResponse = await apiCall<any>("/analytics/dashboard/")
      
      console.log('REST API response status:', restResponse.status)
      
      if (restResponse.data) {
        console.log('Analytics data received:', restResponse.data)
        setAnalytics(restResponse.data)
        return
      }
      
      if (restResponse.status === 401) {
        console.error('Authentication failed. Token might be invalid.')
      }
      
      // If REST fails, set empty analytics to show dashboard
      console.log('Setting empty analytics')
      setAnalytics({
        total_transactions: 0,
        total_volume: 0,
        success_rate: 0,
        average_transaction_size: 0,
        transactions_by_provider: {},
        transactions_by_status: {},
        daily_volume: []
      })
    }

    fetchAnalytics()
    const interval = setInterval(fetchAnalytics, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])

  // Real-time Socket.IO updates
  const { isConnected } = useDashboardSocketIO({
    onAnalyticsUpdate: (data) => {
      console.log('Analytics update received:', data)
      setAnalytics((prev) => prev ? { ...prev, ...data } : data)
    },
    onTransactionUpdate: async (data) => {
      console.log('Transaction update received:', data)
      // Refresh analytics when transaction updates
      const restResponse = await apiCall<any>("/analytics/dashboard/")
      if (restResponse.data) {
        setAnalytics(restResponse.data)
      }
    },
    onError: (error) => {
      console.error('Dashboard Socket.IO error:', error)
    },
  })



  if (!analytics) {
    return <div className="p-8 text-foreground">Loading analytics...</div>
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Real-time payment analytics and insights</p>
      </div>

      {/* Connection Status - Subtle indicator */}
      {isConnected && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </div>
          <Activity className="h-4 w-4 text-green-500" />
        </div>
      )}

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
            <div className="text-2xl font-bold text-green-500">{analytics.success_rate.toFixed(1)}%</div>
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

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/unified-payment"
              className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border hover:border-primary transition-colors"
            >
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-primary" />
              </div>
              <div>
                <div className="font-semibold">Create Payment</div>
                <div className="text-sm text-muted-foreground">Unified gateway</div>
              </div>
            </a>
            <a
              href="/transactions"
              className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border hover:border-primary transition-colors"
            >
              <div className="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <div className="font-semibold">View Transactions</div>
                <div className="text-sm text-muted-foreground">All payments</div>
              </div>
            </a>
            <a
              href="/analytics"
              className="flex items-center gap-3 p-4 bg-card rounded-lg border border-border hover:border-primary transition-colors"
            >
              <div className="h-10 w-10 rounded-full bg-green-500/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <div className="font-semibold">View Analytics</div>
                <div className="text-sm text-muted-foreground">Insights & reports</div>
              </div>
            </a>
          </div>
        </CardContent>
      </Card>

      {/* Recent Transactions */}
      <RecentTransactions />

      {/* Bottom Grid - Activity, Settlement, System Health, User Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeed />
        <SettlementSummary />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemHealth />
        <UserSummary />
      </div>
    </div>
  )
}
