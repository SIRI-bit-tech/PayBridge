"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { apiCall } from "@/lib/api"
import { Activity, Zap, Clock, CheckCircle2 } from "lucide-react"

interface SystemMetrics {
  webhook_delivery_rate: number
  avg_response_time: number
  uptime_percentage: number
  total_requests_today: number
  failed_requests_today: number
}

export function SystemHealth() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchMetrics = async () => {
    const response = await apiCall<SystemMetrics>("/system-analytics/system-health/")
    if (response.data) {
      setMetrics(response.data)
    }
    setLoading(false)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Loading system metrics...</div>
        </CardContent>
      </Card>
    )
  }

  if (!metrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">No metrics available</div>
        </CardContent>
      </Card>
    )
  }

  const getHealthColor = (value: number) => {
    if (value >= 95) return "text-green-500"
    if (value >= 80) return "text-yellow-500"
    return "text-red-500"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span>Webhook Delivery Rate</span>
            </div>
            <span className={`font-bold ${getHealthColor(metrics.webhook_delivery_rate)}`}>
              {metrics.webhook_delivery_rate.toFixed(1)}%
            </span>
          </div>
          <Progress value={metrics.webhook_delivery_rate} className="h-2" />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
              <span>System Uptime</span>
            </div>
            <span className={`font-bold ${getHealthColor(metrics.uptime_percentage)}`}>
              {metrics.uptime_percentage.toFixed(2)}%
            </span>
          </div>
          <Progress value={metrics.uptime_percentage} className="h-2" />
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Avg Response Time
            </div>
            <div className="text-xl font-bold">{metrics.avg_response_time}ms</div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Zap className="h-4 w-4" />
              Requests Today
            </div>
            <div className="text-xl font-bold">{metrics.total_requests_today.toLocaleString()}</div>
          </div>
        </div>

        {metrics.failed_requests_today > 0 && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <div className="text-sm text-red-500">
              {metrics.failed_requests_today} failed requests today
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
