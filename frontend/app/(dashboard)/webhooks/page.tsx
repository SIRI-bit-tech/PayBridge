"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { WebhookSubscription, WebhookDashboard, WebhookDeliveryLog } from "@/types"
import {
  getWebhookSubscriptions,
  createWebhookSubscription,
  deleteWebhookSubscription,
  testWebhookSubscription,
  toggleWebhookSubscription,
  rotateWebhookSecret,
  getWebhookDashboard,
  getWebhookDeliveryLogs,
  retryWebhookDelivery,
} from "@/lib/api"
import { toast } from "sonner"
import { Plus } from "lucide-react"
import { WebhookCard } from "@/components/webhooks/WebhookCard"
import { WebhookFormDialog } from "@/components/webhooks/WebhookFormDialog"
import { WebhookStats } from "@/components/webhooks/WebhookStats"
import { DeliveryLogsTable } from "@/components/webhooks/DeliveryLogsTable"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useWebhookSocket } from "@/hooks/useWebhookSocket"

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<WebhookSubscription[]>([])
  const [stats, setStats] = useState<WebhookDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [logsDialogOpen, setLogsDialogOpen] = useState(false)
  const [selectedWebhookId, setSelectedWebhookId] = useState<string | null>(null)
  const [deliveryLogs, setDeliveryLogs] = useState<WebhookDeliveryLog[]>([])

  const { connected, deliveryUpdates } = useWebhookSocket()

  useEffect(() => {
    loadData()
  }, [])

  // Real-time updates
  useEffect(() => {
    if (deliveryUpdates.length > 0) {
      // Refresh stats when new delivery updates come in
      loadStats()
    }
  }, [deliveryUpdates])

  const loadData = async () => {
    setLoading(true)
    await Promise.all([loadWebhooks(), loadStats()])
    setLoading(false)
  }

  const loadWebhooks = async () => {
    const response = await getWebhookSubscriptions()
    if (response.data) {
      setWebhooks(response.data as WebhookSubscription[])
    }
  }

  const loadStats = async () => {
    const response = await getWebhookDashboard()
    if (response.data) {
      setStats(response.data as WebhookDashboard)
    }
  }

  const handleCreate = async (data: { url: string; selected_events: string[] }) => {
    const response = await createWebhookSubscription(data)
    if (response.data) {
      toast.success("Webhook endpoint created successfully")
      loadWebhooks()
      loadStats()
    } else {
      toast.error(response.error || "Failed to create webhook")
    }
  }

  const handleTest = async (id: string) => {
    const response = await testWebhookSubscription(id)
    if (response.data) {
      toast.success("Test webhook sent successfully")
    } else {
      toast.error(response.error || "Failed to send test webhook")
    }
  }

  const handleToggle = async (id: string) => {
    const response = await toggleWebhookSubscription(id)
    if (response.data) {
      const data = response.data as { message: string; active: boolean }
      toast.success(data.message)
      loadWebhooks()
    } else {
      toast.error(response.error || "Failed to toggle webhook")
    }
  }

  const handleRotateSecret = async (id: string) => {
    const response = await rotateWebhookSecret(id)
    if (response.data) {
      const data = response.data as { message: string; new_secret: string }
      toast.success("Secret key rotated successfully")
      toast.info(`New secret: ${data.new_secret}`, { duration: 10000 })
      loadWebhooks()
    } else {
      toast.error(response.error || "Failed to rotate secret")
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this webhook endpoint?")) return

    const response = await deleteWebhookSubscription(id)
    if (response.status === 204) {
      toast.success("Webhook endpoint deleted")
      loadWebhooks()
      loadStats()
    } else {
      toast.error("Failed to delete webhook")
    }
  }

  const handleViewLogs = async (id: string) => {
    setSelectedWebhookId(id)
    setLogsDialogOpen(true)
    const response = await getWebhookDeliveryLogs(id)
    if (response.data) {
      setDeliveryLogs(response.data as WebhookDeliveryLog[])
    }
  }

  const handleRetryDelivery = async (deliveryId: string) => {
    const response = await retryWebhookDelivery(deliveryId)
    if (response.data) {
      toast.success("Delivery retry queued")
      if (selectedWebhookId) {
        handleViewLogs(selectedWebhookId)
      }
    } else {
      toast.error(response.error || "Failed to retry delivery")
    }
  }

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-sm text-muted-foreground">Loading webhooks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Webhooks</h1>
          <p className="text-muted-foreground">
            Manage webhook endpoints and monitor delivery status
            {connected && <span className="ml-2 text-green-500">● Live</span>}
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Webhook
        </Button>
      </div>

      {stats && <WebhookStats stats={stats} />}

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Webhook Endpoints</h2>
        {webhooks.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center">
            <p className="text-lg font-medium">No webhook endpoints yet</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Create your first webhook endpoint to start receiving real-time events
            </p>
            <Button className="mt-4" onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Webhook
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {webhooks.map((webhook) => (
              <WebhookCard
                key={webhook.id}
                webhook={webhook}
                onTest={handleTest}
                onToggle={handleToggle}
                onRotateSecret={handleRotateSecret}
                onDelete={handleDelete}
                onViewLogs={handleViewLogs}
              />
            ))}
          </div>
        )}
      </div>

      <WebhookFormDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSubmit={handleCreate}
      />

      <Dialog open={logsDialogOpen} onOpenChange={setLogsDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Delivery Logs</DialogTitle>
            <DialogDescription>View webhook delivery attempts and status</DialogDescription>
          </DialogHeader>
          <DeliveryLogsTable logs={deliveryLogs} onRetry={handleRetryDelivery} />
        </DialogContent>
      </Dialog>
    </div>
  )
}
