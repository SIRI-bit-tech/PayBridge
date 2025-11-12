"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface UsageDisplayProps {
  usage: {
    api_calls_used: number
    api_calls_remaining: number
    api_calls_limit: number
    webhooks_used: number
    webhooks_limit: number
    analytics_requests: number
  }
  showAlert?: boolean
}

export function UsageDisplay({ usage, showAlert = false }: UsageDisplayProps) {
  const apiUsagePercent = (usage.api_calls_used / usage.api_calls_limit) * 100
  const webhookUsagePercent = (usage.webhooks_used / usage.webhooks_limit) * 100
  
  const isApiLimitNear = apiUsagePercent >= 80
  const isApiLimitReached = apiUsagePercent >= 100
  const isWebhookLimitReached = webhookUsagePercent >= 100

  return (
    <div className="space-y-4">
      {showAlert && (isApiLimitReached || isWebhookLimitReached) && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {isApiLimitReached && "You've reached your API call limit. "}
            {isWebhookLimitReached && "You've reached your webhook limit. "}
            Please upgrade your plan to continue.
          </AlertDescription>
        </Alert>
      )}

      {showAlert && isApiLimitNear && !isApiLimitReached && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            You're approaching your API call limit ({apiUsagePercent.toFixed(0)}% used).
            Consider upgrading your plan.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Current Usage</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* API Calls */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">API Calls</span>
              <span className="font-medium">
                {usage.api_calls_used.toLocaleString()} / {usage.api_calls_limit.toLocaleString()}
              </span>
            </div>
            <Progress 
              value={apiUsagePercent} 
              className={isApiLimitReached ? "bg-red-200" : isApiLimitNear ? "bg-yellow-200" : ""}
            />
            <p className="text-xs text-muted-foreground">
              {usage.api_calls_remaining.toLocaleString()} calls remaining
            </p>
          </div>

          {/* Webhooks */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Webhooks</span>
              <span className="font-medium">
                {usage.webhooks_used} / {usage.webhooks_limit}
              </span>
            </div>
            <Progress 
              value={webhookUsagePercent}
              className={isWebhookLimitReached ? "bg-red-200" : ""}
            />
          </div>

          {/* Analytics Requests */}
          {usage.analytics_requests > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Analytics Requests</span>
                <span className="font-medium">
                  {usage.analytics_requests.toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
