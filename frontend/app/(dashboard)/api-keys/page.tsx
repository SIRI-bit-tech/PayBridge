"use client"

import { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Plus, Key, Activity, AlertCircle } from "lucide-react"
import { getApiKeys, getApiKeyActivity } from "@/lib/api"
import type { APIKey, APIKeyActivity } from "@/types"
import { GenerateKeyModal } from "@/components/api-keys/GenerateKeyModal"
import { ApiKeyCard } from "@/components/api-keys/ApiKeyCard"
import { useApiKeysSocketIO } from "@/lib/useApiKeysSocketIO"

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>([])
  const [activity, setActivity] = useState<APIKeyActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [error, setError] = useState("")

  // Socket.IO event handlers (memoized)
  const handleKeyCreated = useCallback((data: any) => {
    console.log("API key created via Socket.IO:", data)
    setKeys((prev) => {
      const exists = prev.find((k) => k.id === data.id)
      if (exists) return prev
      return [data, ...prev]
    })
  }, [])

  const handleKeyRevoked = useCallback((data: any) => {
    console.log("API key revoked via Socket.IO:", data)
    setKeys((prev) =>
      prev.map((k) =>
        k.id === data.id ? { ...k, status: "revoked" as const } : k
      )
    )
  }, [])

  const handleKeyUsed = useCallback((data: any) => {
    console.log("API key used via Socket.IO:", data)
    setKeys((prev) =>
      prev.map((k) =>
        k.id === data.id ? { ...k, last_used: data.last_used } : k
      )
    )
  }, [])

  const handleError = useCallback((error: Error) => {
    console.error("Socket.IO error:", error)
  }, [])

  // Real-time Socket.IO connection
  const { isConnected } = useApiKeysSocketIO({
    onKeyCreated: handleKeyCreated,
    onKeyRevoked: handleKeyRevoked,
    onKeyUsed: handleKeyUsed,
    onError: handleError,
  })

  useEffect(() => {
    fetchKeys()
    fetchActivity()
  }, [])

  const fetchKeys = async () => {
    setLoading(true)
    setError("")
    
    try {
      const response = await getApiKeys()
      if (response.data) {
        setKeys(response.data as APIKey[])
      } else if (response.error) {
        setError(response.error)
      }
    } catch (err) {
      setError("Failed to load API keys")
    } finally {
      setLoading(false)
    }
  }

  const fetchActivity = async () => {
    try {
      const response = await getApiKeyActivity()
      if (response.data) {
        setActivity(response.data as APIKeyActivity[])
      }
    } catch (err) {
      console.error("Failed to load API key activity:", err)
    }
  }

  const handleKeyGenerated = (newKey: APIKey) => {
    setKeys((prev) => [newKey, ...prev])
    fetchActivity() // Refresh activity
  }

  const handleKeyRevokedLocal = (id: string) => {
    setKeys((prev) =>
      prev.map((k) => (k.id === id ? { ...k, status: "revoked" as const } : k))
    )
  }

  const activeKeys = keys.filter((k) => k.status === "active")
  const revokedKeys = keys.filter((k) => k.status === "revoked")

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">API Keys</h1>
          <p className="text-muted-foreground mt-1">
            Manage your API keys for authenticating requests to PayBridge
          </p>
        </div>
        <Button onClick={() => setShowGenerateModal(true)} size="lg">
          <Plus className="h-4 w-4 mr-2" />
          Generate New Key
        </Button>
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

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardDescription>Total Keys</CardDescription>
            <CardTitle className="text-3xl">{keys.length}</CardTitle>
          </CardHeader>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardDescription>Active Keys</CardDescription>
            <CardTitle className="text-3xl text-green-500">
              {activeKeys.length}
            </CardTitle>
          </CardHeader>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-3">
            <CardDescription>Total API Calls (30d)</CardDescription>
            <CardTitle className="text-3xl">
              {activity.reduce((sum, a) => sum + a.total_calls, 0).toLocaleString()}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Active Keys */}
      {loading ? (
        <Card className="bg-card border-border">
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">Loading API keys...</p>
          </CardContent>
        </Card>
      ) : activeKeys.length === 0 && revokedKeys.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="p-12 text-center">
            <Key className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No API Keys Yet</h3>
            <p className="text-muted-foreground mb-6">
              Generate your first API key to start making authenticated requests to PayBridge
            </p>
            <Button onClick={() => setShowGenerateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Generate Your First Key
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {activeKeys.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Active Keys</h2>
              <div className="grid gap-4">
                {activeKeys.map((key) => (
                  <ApiKeyCard
                    key={key.id}
                    apiKey={key}
                    onRevoked={handleKeyRevokedLocal}
                  />
                ))}
              </div>
            </div>
          )}

          {revokedKeys.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-muted-foreground">
                Revoked Keys
              </h2>
              <div className="grid gap-4">
                {revokedKeys.map((key) => (
                  <ApiKeyCard
                    key={key.id}
                    apiKey={key}
                    onRevoked={handleKeyRevokedLocal}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* API Usage Documentation */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Using Your API Keys</CardTitle>
          <CardDescription>
            Include your API key in the Authorization header of your requests
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm font-medium mb-2">Example Request:</p>
            <pre className="bg-muted p-4 rounded-md overflow-x-auto text-sm">
              <code>{`curl -X POST https://api.paybridge.com/v1/payments \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 10000,
    "currency": "NGN",
    "provider": "paystack",
    "customer_email": "customer@example.com"
  }'`}</code>
            </pre>
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Security Best Practices:</strong>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Never expose your API keys in client-side code or public repositories</li>
                <li>Use environment variables to store API keys</li>
                <li>Rotate keys regularly and revoke unused keys</li>
                <li>Use different keys for development and production environments</li>
              </ul>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Generate Key Modal */}
      <GenerateKeyModal
        open={showGenerateModal}
        onOpenChange={setShowGenerateModal}
        onKeyGenerated={handleKeyGenerated}
      />
    </div>
  )
}
