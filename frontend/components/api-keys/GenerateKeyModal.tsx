"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Copy, Check, AlertCircle } from "lucide-react"
import { createApiKey } from "@/lib/api"

interface GenerateKeyModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onKeyGenerated: (key: any) => void
}

export function GenerateKeyModal({ open, onOpenChange, onKeyGenerated }: GenerateKeyModalProps) {
  const [label, setLabel] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [generatedKey, setGeneratedKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    if (!label.trim()) {
      setError("Please enter a label for your API key")
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await createApiKey(label.trim())
      
      if (response.data && typeof response.data === 'object' && 'key' in response.data) {
        setGeneratedKey(response.data.key as string)
        onKeyGenerated(response.data)
      } else if (response.error) {
        setError(response.error)
      }
    } catch (err) {
      setError("Failed to generate API key. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (generatedKey) {
      await navigator.clipboard.writeText(generatedKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleClose = () => {
    setLabel("")
    setGeneratedKey(null)
    setError("")
    setCopied(false)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Generate New API Key</DialogTitle>
          <DialogDescription>
            {generatedKey 
              ? "Copy your API key now. You won't be able to see it again!"
              : "Create a new API key to authenticate your requests to PayBridge."}
          </DialogDescription>
        </DialogHeader>

        {!generatedKey ? (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="label">Label</Label>
              <Input
                id="label"
                placeholder="e.g., Production, Testing, Mobile App"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                disabled={loading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !loading) {
                    handleGenerate()
                  }
                }}
              />
              <p className="text-sm text-muted-foreground">
                Give your API key a descriptive name to identify its usage
              </p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        ) : (
          <div className="space-y-4 py-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>Important:</strong> Copy this key now. For security reasons, you won't be able to see it again.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label>Your API Key</Label>
              <div className="flex gap-2">
                <Input
                  value={generatedKey}
                  readOnly
                  className="font-mono text-sm"
                />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={handleCopy}
                  className="flex-shrink-0"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div className="bg-muted p-3 rounded-md">
              <p className="text-sm font-medium mb-1">Usage Example:</p>
              <code className="text-xs block bg-background p-2 rounded">
                curl -H "Authorization: Bearer {generatedKey.substring(0, 20)}..." \<br />
                &nbsp;&nbsp;https://api.paybridge.com/v1/payments
              </code>
            </div>
          </div>
        )}

        <DialogFooter>
          {!generatedKey ? (
            <>
              <Button variant="outline" onClick={handleClose} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={handleGenerate} disabled={loading || !label.trim()}>
                {loading ? "Generating..." : "Generate Key"}
              </Button>
            </>
          ) : (
            <Button onClick={handleClose} className="w-full">
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
