"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Copy, MoreVertical, Trash2, Check, Key } from "lucide-react"
import type { APIKey } from "@/types"
import { revokeApiKey } from "@/lib/api"

interface ApiKeyCardProps {
  apiKey: APIKey
  onRevoked: (id: string) => void
}

export function ApiKeyCard({ apiKey, onRevoked }: ApiKeyCardProps) {
  const [copied, setCopied] = useState(false)
  const [showRevokeDialog, setShowRevokeDialog] = useState(false)
  const [revoking, setRevoking] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(apiKey.masked_key)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRevoke = async () => {
    setRevoking(true)
    try {
      const response = await revokeApiKey(apiKey.id)
      if (response.status === 200) {
        onRevoked(apiKey.id)
        setShowRevokeDialog(false)
      }
    } catch (error) {
      console.error("Failed to revoke API key:", error)
    } finally {
      setRevoking(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500/10 text-green-500 border-green-500/20"
      case "revoked":
        return "bg-red-500/10 text-red-500 border-red-500/20"
      case "inactive":
        return "bg-gray-500/10 text-gray-500 border-gray-500/20"
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20"
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  return (
    <>
      <Card className="bg-card border-border hover:border-primary/50 transition-colors">
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Key className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-foreground truncate">
                    {apiKey.label || apiKey.name}
                  </h3>
                  <Badge
                    variant="outline"
                    className={`mt-1 ${getStatusColor(apiKey.status)}`}
                  >
                    {apiKey.status.charAt(0).toUpperCase() + apiKey.status.slice(1)}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 bg-muted p-2 rounded-md">
                  <code className="text-sm font-mono flex-1 truncate">
                    {apiKey.masked_key}
                  </code>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleCopy}
                    className="flex-shrink-0 h-8 w-8 p-0"
                  >
                    {copied ? (
                      <Check className="h-3.5 w-3.5 text-green-500" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </Button>
                </div>

                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>Created {formatDate(apiKey.created_at)}</span>
                  {apiKey.last_used && (
                    <>
                      <span>•</span>
                      <span>Last used {formatDate(apiKey.last_used)}</span>
                    </>
                  )}
                  {!apiKey.last_used && (
                    <>
                      <span>•</span>
                      <span>Never used</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {apiKey.status === "active" && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="flex-shrink-0">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    className="text-destructive focus:text-destructive"
                    onClick={() => setShowRevokeDialog(true)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Revoke Key
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={showRevokeDialog} onOpenChange={setShowRevokeDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke API Key?</AlertDialogTitle>
            <AlertDialogDescription>
              This will immediately invalidate the API key "{apiKey.label || apiKey.name}".
              Any applications using this key will no longer be able to authenticate.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={revoking}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRevoke}
              disabled={revoking}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {revoking ? "Revoking..." : "Revoke Key"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
