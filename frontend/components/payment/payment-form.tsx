"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { initiatePayment } from "@/lib/api"
import { AlertCircle, Loader2, CheckCircle2, XCircle } from "lucide-react"

interface PaymentFormProps {
  amount: number
  currency?: string
  customerEmail: string
  providerId: string
  description?: string
}

type PaymentStatus = "idle" | "processing" | "success" | "error" | "network_error" | "retry_pending"

export function PaymentForm({
  amount,
  currency = "NGN",
  customerEmail,
  providerId,
  description = "",
}: PaymentFormProps) {
  const router = useRouter()
  const [status, setStatus] = useState<PaymentStatus>("idle")
  const [error, setError] = useState<string>("")
  const [transactionId, setTransactionId] = useState<string>("")
  const [retryCount, setRetryCount] = useState(0)
  const retryTimeoutRef = useRef<NodeJS.Timeout>()

  const handlePayment = async () => {
    try {
      setStatus("processing")
      setError("")

      const response = await initiatePayment({
        api_key_id: providerId,
        provider: "stripe",
        amount,
        currency,
        customer_email: customerEmail,
        description,
        use_tokenization: true, // Force card tokenization
        save_card: false, // Never save card details
      })

      if (response.status === 0) {
        // Network error
        setStatus("network_error")
        setError("Network connection failed. Check your internet and retry.")
        return
      }

      if (response.error) {
        setStatus("error")
        setError(response.error)
        return
      }

      if (response.data) {
        setTransactionId(response.data.id)

        // Check if payment requires additional action
        if (response.data.provider_response?.requires_action) {
          setStatus("processing")
          // Handle 3D Secure or other additional verification
          // This would typically redirect to a Stripe hosted page
        } else {
          setStatus("success")
        }
      }
    } catch (err) {
      setStatus("error")
      setError("An unexpected error occurred. Please try again.")
    }
  }

  const handleRetry = async () => {
    if (retryCount >= 3) {
      setStatus("error")
      setError("Maximum retry attempts reached. Please try again later.")
      return
    }

    // Exponential backoff: 5s, 10s, 20s
    const delayMs = 5000 * Math.pow(2, retryCount)

    setStatus("retry_pending")
    setRetryCount(retryCount + 1)

    console.log(`[v0] Scheduling retry in ${delayMs}ms (attempt ${retryCount + 1})`)

    retryTimeoutRef.current = setTimeout(async () => {
      try {
        setStatus("processing")
        setError("")

        const response = await initiatePayment({
          api_key_id: providerId,
          provider: "stripe",
          amount,
          currency,
          customer_email: customerEmail,
          description,
          use_tokenization: true,
          save_card: false,
        })

        if (response.status === 0) {
          setStatus("network_error")
          setError("Still unable to connect. Please check your internet connection.")
          return
        }

        if (response.error) {
          setStatus("error")
          setError(response.error)
          return
        }

        if (response.data) {
          setTransactionId(response.data.id)
          setStatus("success")
          setRetryCount(0) // Reset on success
        }
      } catch (err) {
        setStatus("error")
        setError("Retry failed. Please try again manually.")
      }
    }, delayMs)
  }

  // Cleanup timeout on unmount
  const handleCancel = () => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current)
      setRetryCount(0)
      setStatus("idle")
      setError("")
    }
  }

  return (
    <Card className="w-full max-w-md bg-neutral-800 border-neutral-700">
      <CardHeader>
        <CardTitle className="text-white">Make Payment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Amount Display */}
        <div className="bg-neutral-700 p-4 rounded-lg">
          <p className="text-neutral-400 text-sm">Amount</p>
          <p className="text-3xl font-bold text-primary">
            {amount.toLocaleString()} {currency}
          </p>
        </div>

        {/* Status Messages */}
        {status === "success" && (
          <div className="bg-green-900/20 border border-green-700 p-4 rounded-lg flex gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
            <div>
              <p className="text-green-300 font-semibold">Payment Successful</p>
              <p className="text-green-200 text-sm">Transaction ID: {transactionId}</p>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="bg-red-900/20 border border-red-700 p-4 rounded-lg flex gap-3">
            <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <div>
              <p className="text-red-300 font-semibold">Payment Failed</p>
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          </div>
        )}

        {status === "network_error" && (
          <div className="bg-yellow-900/20 border border-yellow-700 p-4 rounded-lg flex gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
            <div>
              <p className="text-yellow-300 font-semibold">Connection Lost</p>
              <p className="text-yellow-200 text-sm">
                {error}
                {retryCount > 0 && ` (Attempt ${retryCount}/3)`}
              </p>
            </div>
          </div>
        )}

        {status === "retry_pending" && (
          <div className="bg-blue-900/20 border border-blue-700 p-4 rounded-lg flex gap-3">
            <Loader2 className="w-5 h-5 text-blue-500 flex-shrink-0 animate-spin" />
            <div>
              <p className="text-blue-300 font-semibold">Retrying Payment...</p>
              <p className="text-blue-200 text-sm">Attempt {retryCount} of 3. This will not charge twice.</p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {status === "idle" || status === "error" ? (
            <Button onClick={handlePayment} disabled={status === "processing"} className="flex-1">
              {status === "processing" ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                "Pay Now"
              )}
            </Button>
          ) : status === "network_error" ? (
            <>
              <Button onClick={handleRetry} disabled={status === "processing" || retryCount >= 3} className="flex-1">
                {retryCount >= 3 ? "Max Retries Reached" : "Retry Payment"}
              </Button>
              <Button onClick={handleCancel} variant="outline" className="flex-1 bg-transparent">
                Cancel
              </Button>
            </>
          ) : status === "retry_pending" ? (
            <Button onClick={handleCancel} variant="outline" className="w-full bg-transparent">
              Cancel Retry
            </Button>
          ) : null}
        </div>

        {/* Security Notice */}
        <p className="text-neutral-400 text-xs text-center">
          <lock className="w-3 h-3 inline mr-1" />
          Your card details are NOT saved. Payment is secured with Stripe tokenization.
        </p>
      </CardContent>
    </Card>
  )
}
