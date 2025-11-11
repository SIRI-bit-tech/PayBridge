"use client"

import { useState } from "react"
import Image from "next/image"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { CreditCard, Loader2 } from "lucide-react"

interface ProviderSelectionModalProps {
  open: boolean
  onClose: () => void
  onSelect: (provider: string) => Promise<void>
  planName: string
  amount: number
  currency: string
}

const PROVIDERS = [
  {
    id: "stripe",
    name: "Stripe",
    description: "Credit/Debit Card, Apple Pay, Google Pay",
    logo: "https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg",
  },
  {
    id: "paystack",
    name: "Paystack",
    description: "Card, Bank Transfer, USSD, Mobile Money",
    logo: "https://paystack.com/assets/img/logo/paystack-icon-blue.png",
  },
  {
    id: "flutterwave",
    name: "Flutterwave",
    description: "Card, Bank, Mobile Money, USSD",
    logo: "https://flutterwave.com/images/logo/full.svg",
  },
]

export function ProviderSelectionModal({
  open,
  onClose,
  onSelect,
  planName,
  amount,
  currency,
}: ProviderSelectionModalProps) {
  const [selectedProvider, setSelectedProvider] = useState<string>("stripe")
  const [loading, setLoading] = useState(false)

  const handleContinue = async () => {
    setLoading(true)
    try {
      await onSelect(selectedProvider)
    } catch (error) {
      console.error("Payment error:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Select Payment Provider</DialogTitle>
          <DialogDescription>
            Choose your preferred payment method for {planName} plan
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Plan Summary */}
          <div className="bg-muted p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm text-muted-foreground">Plan</p>
                <p className="font-semibold">{planName}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Amount</p>
                <p className="text-2xl font-bold text-primary">
                  {currency} {amount}
                </p>
              </div>
            </div>
          </div>

          {/* Provider Selection */}
          <RadioGroup value={selectedProvider} onValueChange={setSelectedProvider}>
            <div className="space-y-3">
              {PROVIDERS.map((provider) => (
                <div
                  key={provider.id}
                  className={`flex items-center space-x-3 border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedProvider === provider.id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                  onClick={() => setSelectedProvider(provider.id)}
                >
                  <RadioGroupItem value={provider.id} id={provider.id} />
                  <div className="flex-1">
                    <Label
                      htmlFor={provider.id}
                      className="flex items-center gap-3 cursor-pointer"
                    >
                      <div className="relative w-12 h-12 flex items-center justify-center bg-white rounded-lg p-2 border border-gray-200">
                        <Image
                          src={provider.logo}
                          alt={`${provider.name} logo`}
                          width={40}
                          height={40}
                          className="object-contain"
                        />
                      </div>
                      <div>
                        <p className="font-semibold">{provider.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {provider.description}
                        </p>
                      </div>
                    </Label>
                  </div>
                </div>
              ))}
            </div>
          </RadioGroup>

          {/* Security Notice */}
          <div className="flex items-start gap-2 text-sm text-muted-foreground bg-muted p-3 rounded-lg">
            <CreditCard className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <p>
              Your payment information is securely processed by our payment partners.
              We never store your card details.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} className="flex-1" disabled={loading}>
              Cancel
            </Button>
            <Button onClick={handleContinue} className="flex-1" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                "Continue to Payment"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
