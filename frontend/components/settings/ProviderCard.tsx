"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  CheckCircle2, XCircle, AlertCircle, Loader2, 
  Eye, EyeOff, Trash2, ToggleLeft, ToggleRight, Star 
} from "lucide-react"
import type { PaymentProviderConfig } from "@/types"
import { ProviderLogo } from "./ProviderLogo"

interface ProviderCardProps {
  provider: PaymentProviderConfig
  onValidate: (id: string) => Promise<void>
  onToggleMode: (id: string) => Promise<void>
  onSetPrimary: (id: string) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

export function ProviderCard({ 
  provider, 
  onValidate, 
  onToggleMode, 
  onSetPrimary, 
  onDelete 
}: ProviderCardProps) {
  const [showKeys, setShowKeys] = useState(false)
  const [loading, setLoading] = useState<string | null>(null)

  const handleAction = async (action: string, fn: () => Promise<void>) => {
    setLoading(action)
    try {
      await fn()
    } finally {
      setLoading(null)
    }
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center">
              <ProviderLogo provider={provider.provider} size="lg" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-lg capitalize">{provider.provider}</h3>
                {provider.is_primary && (
                  <Badge variant="default" className="gap-1">
                    <Star className="w-3 h-3" />
                    Primary
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={provider.mode === "live" ? "destructive" : "secondary"}>
                  {provider.mode === "live" ? "Live Mode" : "Test Mode"}
                </Badge>
                <Badge variant={provider.is_active ? "default" : "outline"}>
                  {provider.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {provider.credentials_validated ? (
              <CheckCircle2 className="w-5 h-5 text-green-500" />
            ) : provider.validation_error ? (
              <XCircle className="w-5 h-5 text-red-500" />
            ) : (
              <AlertCircle className="w-5 h-5 text-yellow-500" />
            )}
          </div>
        </div>

        <div className="space-y-3 mb-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-muted-foreground">Public Key</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowKeys(!showKeys)}
              >
                {showKeys ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
            </div>
            <code className="text-xs bg-muted px-2 py-1 rounded block">
              {showKeys ? provider.public_key_masked : "••••••••••••"}
            </code>
          </div>
          
          <div>
            <span className="text-sm text-muted-foreground">Secret Key</span>
            <code className="text-xs bg-muted px-2 py-1 rounded block mt-1">
              {showKeys ? provider.secret_key_masked : "••••••••••••"}
            </code>
          </div>

          {provider.validation_error && (
            <div className="text-xs text-red-500 bg-red-50 dark:bg-red-950 p-2 rounded">
              {provider.validation_error}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleAction("validate", () => onValidate(provider.id))}
            disabled={loading === "validate"}
          >
            {loading === "validate" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              "Validate"
            )}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleAction("toggle", () => onToggleMode(provider.id))}
            disabled={loading === "toggle"}
          >
            {loading === "toggle" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                {provider.mode === "test" ? <ToggleRight className="w-4 h-4 mr-1" /> : <ToggleLeft className="w-4 h-4 mr-1" />}
                Switch to {provider.mode === "test" ? "Live" : "Test"}
              </>
            )}
          </Button>
          
          {!provider.is_primary && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleAction("primary", () => onSetPrimary(provider.id))}
              disabled={loading === "primary"}
            >
              {loading === "primary" ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Star className="w-4 h-4 mr-1" />
                  Set Primary
                </>
              )}
            </Button>
          )}
          
          <Button
            variant="destructive"
            size="sm"
            onClick={() => handleAction("delete", () => onDelete(provider.id))}
            disabled={loading === "delete"}
          >
            {loading === "delete" ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
