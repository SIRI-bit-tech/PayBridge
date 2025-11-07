"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { getWebhooks, createWebhook, deleteWebhook } from "@/lib/api"
import type { Webhook } from "@/types"

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [url, setUrl] = useState("")
  const [selectedEvents, setSelectedEvents] = useState<string[]>([])

  const events = [
    "payment.completed",
    "payment.failed",
    "payment.pending",
    "refund.initiated",
    "kyc.verified",
    "kyc.failed",
  ]

  useEffect(() => {
    fetchWebhooks()
  }, [])

  const fetchWebhooks = async () => {
    setLoading(true)
    const response = await getWebhooks()
    if (response.data) {
      setWebhooks(response.data as Webhook[])
    }
    setLoading(false)
  }

  const handleCreateWebhook = async () => {
    if (!url.trim() || selectedEvents.length === 0) return

    setCreating(true)
    const response = await createWebhook({ url, event_types: selectedEvents })
    if (response.data) {
      setWebhooks([...webhooks, response.data as Webhook])
      setUrl("")
      setSelectedEvents([])
    }
    setCreating(false)
  }

  const handleDeleteWebhook = async (id: string) => {
    const response = await deleteWebhook(id)
    if (response.status === 204) {
      setWebhooks(webhooks.filter((w) => w.id !== id))
    }
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Webhooks</h1>
        <p className="text-neutral-400">Receive real-time payment events</p>
      </div>

      {/* Create Webhook */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Create Webhook Endpoint</CardTitle>
          <CardDescription>Subscribe to payment and KYC events</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            type="url"
            placeholder="https://example.com/webhooks/paybridge"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="bg-background border-border"
          />

          <div>
            <label className="text-foreground text-sm font-medium mb-2 block">Subscribe to events:</label>
            <div className="grid grid-cols-2 gap-3">
              {events.map((event) => (
                <label key={event} className="flex items-center gap-2 text-neutral-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(event)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedEvents([...selectedEvents, event])
                      } else {
                        setSelectedEvents(selectedEvents.filter((e) => e !== event))
                      }
                    }}
                    className="rounded"
                  />
                  {event}
                </label>
              ))}
            </div>
          </div>

          <Button onClick={handleCreateWebhook} disabled={creating || !url.trim() || selectedEvents.length === 0}>
            {creating ? "Creating..." : "Create Webhook"}
          </Button>
        </CardContent>
      </Card>

      {/* Webhooks List */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Active Webhooks</CardTitle>
          <CardDescription>
            {webhooks.length} endpoint{webhooks.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-neutral-400">Loading...</p>
          ) : webhooks.length === 0 ? (
            <p className="text-neutral-400">No webhooks configured yet</p>
          ) : (
            <div className="space-y-4">
              {webhooks.map((webhook) => (
                <div key={webhook.id} className="bg-muted rounded p-4 border border-border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-mono text-sm text-primary break-all">{webhook.url}</h3>
                      <p className="text-sm text-neutral-400 mt-2">
                        Status:{" "}
                        <span className={webhook.is_active ? "text-green-400" : "text-red-400"}>
                          {webhook.is_active ? "Active" : "Inactive"}
                        </span>
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {webhook.event_types.map((event) => (
                          <span
                            key={event}
                            className="inline-block bg-primary/20 text-primary px-2 py-1 rounded text-xs"
                          >
                            {event}
                          </span>
                        ))}
                      </div>
                      {webhook.last_triggered && (
                        <p className="text-xs text-neutral-500 mt-2">
                          Last triggered: {new Date(webhook.last_triggered).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <Button variant="destructive" size="sm" onClick={() => handleDeleteWebhook(webhook.id)}>
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
