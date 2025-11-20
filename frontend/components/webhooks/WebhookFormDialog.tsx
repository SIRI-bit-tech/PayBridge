"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { WEBHOOK_EVENT_TYPES } from "@/constants"
import { toast } from "sonner"

interface WebhookFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: { url: string; selected_events: string[] }) => Promise<void>
}

export function WebhookFormDialog({ open, onOpenChange, onSubmit }: WebhookFormDialogProps) {
  const [url, setUrl] = useState("")
  const [selectedEvents, setSelectedEvents] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!url) {
      toast.error("Please enter a webhook URL")
      return
    }

    if (selectedEvents.length === 0) {
      toast.error("Please select at least one event type")
      return
    }

    // Validate URL
    try {
      const urlObj = new URL(url)
      if (urlObj.protocol !== 'https:') {
        toast.error("Please enter a valid HTTPS URL")
        return
      }
    } catch {
      toast.error("Please enter a valid HTTPS URL")
      return
    }

    setLoading(true)
    try {
      await onSubmit({ url, selected_events: selectedEvents })
      setUrl("")
      setSelectedEvents([])
      onOpenChange(false)
    } catch (error) {
      console.error("Error creating webhook:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleEvent = (eventType: string) => {
    setSelectedEvents((prev) =>
      prev.includes(eventType) ? prev.filter((e) => e !== eventType) : [...prev, eventType]
    )
  }

  const selectAll = () => {
    setSelectedEvents(WEBHOOK_EVENT_TYPES.map((e) => e.value))
  }

  const deselectAll = () => {
    setSelectedEvents([])
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Webhook Endpoint</DialogTitle>
          <DialogDescription>
            Register a webhook endpoint to receive real-time event notifications
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url">Webhook URL</Label>
            <Input
              id="url"
              type="url"
              placeholder="https://your-app.com/webhooks"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground">
              Must be a valid HTTPS URL that can receive POST requests
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Event Types</Label>
              <div className="flex gap-2">
                <Button type="button" variant="ghost" size="sm" onClick={selectAll}>
                  Select All
                </Button>
                <Button type="button" variant="ghost" size="sm" onClick={deselectAll}>
                  Deselect All
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 rounded-lg border p-4">
              {WEBHOOK_EVENT_TYPES.map((event) => (
                <div key={event.value} className="flex items-start space-x-2">
                  <Checkbox
                    id={event.value}
                    checked={selectedEvents.includes(event.value)}
                    onCheckedChange={() => toggleEvent(event.value)}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <label
                      htmlFor={event.value}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {event.label}
                    </label>
                    <p className="text-xs text-muted-foreground">{event.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Webhook"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
