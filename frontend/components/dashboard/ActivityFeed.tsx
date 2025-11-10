"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useDashboardSocketIO } from "@/lib/useDashboardSocketIO"
import { formatDistanceToNow } from "date-fns"
import { Activity, CheckCircle2, XCircle, AlertCircle, DollarSign } from "lucide-react"

interface ActivityEvent {
  id: string
  type: string
  message: string
  timestamp: string
  status?: string
}

export function ActivityFeed() {
  const [activities, setActivities] = useState<ActivityEvent[]>([])

  const { isConnected } = useDashboardSocketIO({
    onTransactionUpdate: (data: any) => {
      const activity: ActivityEvent = {
        id: data.id || Date.now().toString(),
        type: "transaction",
        message: `New transaction: ${data.currency} ${data.amount} via ${data.provider}`,
        timestamp: new Date().toISOString(),
        status: data.status,
      }
      setActivities((prev) => [activity, ...prev].slice(0, 20))
    },
  })

  const getIcon = (type: string, status?: string) => {
    if (type === "transaction") {
      if (status === "completed") return <CheckCircle2 className="h-4 w-4 text-green-500" />
      if (status === "failed") return <XCircle className="h-4 w-4 text-red-500" />
      return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }
    if (type === "webhook") return <Activity className="h-4 w-4 text-blue-500" />
    if (type === "settlement") return <DollarSign className="h-4 w-4 text-green-500" />
    return <Activity className="h-4 w-4 text-gray-500" />
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Activity Feed</span>
          {isConnected && (
            <div className="flex items-center gap-2 text-xs text-green-500 font-normal">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              Live
            </div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {activities.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              Waiting for activity...
            </div>
          ) : (
            <div className="space-y-4">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3 pb-3 border-b border-border last:border-0">
                  <div className="mt-1">{getIcon(activity.type, activity.status)}</div>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
