"use client"

import { WebhookSubscription } from "@/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { WEBHOOK_HEALTH_STATUS } from "@/constants"
import { Activity, Copy, MoreVertical, Power, RotateCw, TestTube, Trash2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { toast } from "sonner"

interface WebhookCardProps {
  webhook: WebhookSubscription
  onTest: (id: string) => void
  onToggle: (id: string) => void
  onRotateSecret: (id: string) => void
  onDelete: (id: string) => void
  onViewLogs: (id: string) => void
}

export function WebhookCard({
  webhook,
  onTest,
  onToggle,
  onRotateSecret,
  onDelete,
  onViewLogs,
}: WebhookCardProps) {
  const healthStatus = WEBHOOK_HEALTH_STATUS[webhook.health_status]

  const copySecret = () => {
    navigator.clipboard.writeText(webhook.masked_secret)
    toast.success("Secret copied to clipboard")
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <CardTitle className="text-base font-medium">{webhook.url}</CardTitle>
          <CardDescription className="flex items-center gap-2">
            <Badge variant={webhook.active ? "default" : "secondary"}>
              {webhook.active ? "Active" : "Inactive"}
            </Badge>
            <Badge variant="outline" className={`${healthStatus.color} ${healthStatus.bgColor}`}>
              {healthStatus.label}
            </Badge>
          </CardDescription>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onTest(webhook.id)}>
              <TestTube className="mr-2 h-4 w-4" />
              Send Test Event
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onToggle(webhook.id)}>
              <Power className="mr-2 h-4 w-4" />
              {webhook.active ? "Disable" : "Enable"}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onViewLogs(webhook.id)}>
              <Activity className="mr-2 h-4 w-4" />
              View Delivery Logs
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onRotateSecret(webhook.id)}>
              <RotateCw className="mr-2 h-4 w-4" />
              Rotate Secret
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onDelete(webhook.id)} className="text-red-600">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Secret Key</span>
            <div className="flex items-center gap-2">
              <code className="rounded bg-muted px-2 py-1 text-xs">{webhook.masked_secret}</code>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={copySecret}>
                <Copy className="h-3 w-3" />
              </Button>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Events</span>
            <span className="font-medium">{webhook.selected_events.length} selected</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Success Rate</span>
            <span className="font-medium">
              {webhook.success_count + webhook.failure_count > 0
                ? Math.round((webhook.success_count / (webhook.success_count + webhook.failure_count)) * 100)
                : 0}
              %
            </span>
          </div>

          {webhook.last_delivery_at && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Last Delivery</span>
              <span className="font-medium">{new Date(webhook.last_delivery_at).toLocaleString()}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
