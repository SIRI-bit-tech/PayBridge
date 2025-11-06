"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { getApiKeys, createApiKey, revokeApiKey } from "@/lib/api"
import type { APIKey } from "@/types"

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<APIKey[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newKeyName, setNewKeyName] = useState("")

  useEffect(() => {
    fetchKeys()
  }, [])

  const fetchKeys = async () => {
    setLoading(true)
    const response = await getApiKeys()
    if (response.data) {
      setKeys(response.data as APIKey[])
    }
    setLoading(false)
  }

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return

    setCreating(true)
    const response = await createApiKey(newKeyName)
    if (response.data) {
      setKeys([...keys, response.data as APIKey])
      setNewKeyName("")
    }
    setCreating(false)
  }

  const handleRevokeKey = async (id: string) => {
    const response = await revokeApiKey(id)
    if (response.status === 200) {
      setKeys(keys.map((k) => (k.id === id ? { ...k, status: "revoked" as const } : k)))
    }
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">API Keys</h1>
        <p className="text-neutral-400">Manage your API keys for authentication</p>
      </div>

      {/* Create New Key */}
      <Card className="bg-neutral-800 border-neutral-700">
        <CardHeader>
          <CardTitle>Create New API Key</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Input
              placeholder="Key name (e.g., Production, Testing)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="bg-neutral-700 border-neutral-600"
            />
            <Button onClick={handleCreateKey} disabled={creating || !newKeyName.trim()}>
              {creating ? "Creating..." : "Create Key"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* API Keys List */}
      <Card className="bg-neutral-800 border-neutral-700">
        <CardHeader>
          <CardTitle>Active Keys</CardTitle>
          <CardDescription>
            {keys.length} key{keys.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-neutral-400">Loading...</p>
          ) : keys.length === 0 ? (
            <p className="text-neutral-400">No API keys yet. Create one to get started.</p>
          ) : (
            <div className="space-y-4">
              {keys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between bg-neutral-900 rounded p-4 border border-neutral-700"
                >
                  <div>
                    <h3 className="font-semibold text-white">{key.name}</h3>
                    <p className="text-sm text-neutral-400">
                      {key.status} • Created {new Date(key.created_at).toLocaleDateString()}
                    </p>
                    {key.last_used && (
                      <p className="text-xs text-neutral-500">Last used: {new Date(key.last_used).toLocaleString()}</p>
                    )}
                  </div>
                  {key.status === "active" && (
                    <Button variant="destructive" size="sm" onClick={() => handleRevokeKey(key.id)}>
                      Revoke
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
