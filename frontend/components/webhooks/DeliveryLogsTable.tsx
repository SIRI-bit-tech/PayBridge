"use client"

import { WebhookDeliveryLog } from "@/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { WEBHOOK_DELIVERY_STATUS } from "@/constants"
import { RefreshCw } from "lucide-react"

interface DeliveryLogsTableProps {
  logs: WebhookDeliveryLog[]
  onRetry: (id: string) => void
}

export function DeliveryLogsTable({ logs, onRetry }: DeliveryLogsTableProps) {
  if (logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">No delivery logs yet</p>
      </div>
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Event Type</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Attempt</TableHead>
            <TableHead>HTTP Code</TableHead>
            <TableHead>Latency</TableHead>
            <TableHead>Time</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const statusConfig = WEBHOOK_DELIVERY_STATUS[log.status]
            return (
              <TableRow key={log.id}>
                <TableCell className="font-medium">{log.event_type}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={`${statusConfig.color} ${statusConfig.bgColor}`}>
                    {statusConfig.label}
                  </Badge>
                </TableCell>
                <TableCell>{log.attempt_number}</TableCell>
                <TableCell>{log.http_status_code || "-"}</TableCell>
                <TableCell>{log.latency_ms ? `${log.latency_ms}ms` : "-"}</TableCell>
                <TableCell>{new Date(log.created_at).toLocaleString()}</TableCell>
                <TableCell className="text-right">
                  {log.status === "failed" && (
                    <Button variant="ghost" size="sm" onClick={() => onRetry(log.id)}>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Retry
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}
