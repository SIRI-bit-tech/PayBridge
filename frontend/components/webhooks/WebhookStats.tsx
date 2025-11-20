"use client"

import { WebhookDashboard } from "@/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity, AlertTriangle, CheckCircle2, Clock, Webhook } from "lucide-react"

interface WebhookStatsProps {
  stats: WebhookDashboard
}

export function WebhookStats({ stats }: WebhookStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Endpoints</CardTitle>
          <Webhook className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.active_subscriptions}</div>
          <p className="text-xs text-muted-foreground">
            {stats.total_subscriptions} total
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.success_rate.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            Last 24 hours
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{Math.round(stats.avg_latency_ms)}ms</div>
          <p className="text-xs text-muted-foreground">
            Response time
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Failed Deliveries</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.failed_deliveries_24h}</div>
          <p className="text-xs text-muted-foreground">
            {stats.dead_letter_deliveries_24h} dead letter
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
