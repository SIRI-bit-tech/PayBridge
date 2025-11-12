"use client"

import { useEffect, useState, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { getBillingPlan, createSubscription } from "@/lib/api"
import { Check, Loader2, Zap, TrendingUp, Crown } from "lucide-react"
import { useBillingSocketIO } from "@/lib/useBillingSocketIO"
import { ProviderSelectionModal } from "@/components/billing/ProviderSelectionModal"
import { UsageDisplay } from "@/components/billing/UsageDisplay"
import { toast } from "sonner"

interface Plan {
  id: string
  name: string
  tier: string
  price: number
  currency: string
  api_limit: number
  webhook_limit: number
  has_analytics: boolean
  analytics_level: string
  has_priority_support: boolean
  has_custom_branding: boolean
}

interface Subscription {
  id: string
  plan: Plan
  status: string
  start_date: string
  renewal_date: string
  days_until_renewal: number
}

interface Usage {
  api_calls_used: number
  api_calls_remaining: number
  api_calls_limit: number
  webhooks_used: number
  webhooks_limit: number
  analytics_requests: number
}

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [usage, setUsage] = useState<Usage | null>(null)
  const [availablePlans, setAvailablePlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [showProviderModal, setShowProviderModal] = useState(false)

  // Real-time Socket.IO connection
  const { isConnected } = useBillingSocketIO({
    onPlanUpdate: (data) => {
      console.log("Plan updated:", data)
      toast.success("Your plan has been updated!")
      fetchBillingData()
    },
    onUsageUpdate: (data) => {
      console.log("Usage updated:", data)
      setUsage((prev) => ({
        ...prev!,
        ...data,
      }))
    },
    onLimitReached: (data) => {
      console.log("Limit reached:", data)
      toast.error(`You've reached your ${data.resource} limit!`, {
        description: "Please upgrade your plan to continue.",
        action: {
          label: "Upgrade",
          onClick: () => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }),
        },
      })
    },
  })

  useEffect(() => {
    fetchBillingData()
  }, [])

  const fetchBillingData = async () => {
    setLoading(true)
    const response = await getBillingPlan()
    if (response.data) {
      const data = response.data as any
      setSubscription(data.current_subscription)
      setUsage(data.usage)
      setAvailablePlans(data.available_plans)
    }
    setLoading(false)
  }

  const handleUpgradeClick = (plan: Plan) => {
    // Handle Enterprise plan - contact sales
    if (plan.tier === "enterprise") {
      window.location.href = "mailto:sales@paybridge.com?subject=Enterprise Plan Inquiry&body=I'm interested in learning more about the Enterprise plan."
      return
    }
    
    if (plan.price === 0) {
      toast.info("You're already on the Free plan")
      return
    }
    setSelectedPlan(plan)
    setShowProviderModal(true)
  }

  const handleProviderSelect = async (provider: string) => {
    if (!selectedPlan) return

    try {
      const response = await createSubscription(selectedPlan.id, provider)
      
      if (response.data) {
        const data = response.data as any
        const { authorization_url, client_secret } = data

        // Redirect to payment page based on provider
        if (authorization_url) {
          // Paystack or Flutterwave
          window.location.href = authorization_url
        } else if (client_secret) {
          // Stripe - would need Stripe Elements integration
          toast.info("Stripe payment integration coming soon")
        }
      } else {
        toast.error(response.error || "Failed to create payment session")
      }
    } catch (error) {
      console.error("Payment error:", error)
      toast.error("An error occurred while processing your request")
    } finally {
      setShowProviderModal(false)
    }
  }

  const getPlanIcon = (tier: string) => {
    switch (tier) {
      case "free":
        return <Zap className="h-5 w-5" />
      case "starter":
        return <TrendingUp className="h-5 w-5" />
      case "growth":
        return <TrendingUp className="h-5 w-5" />
      case "enterprise":
        return <Crown className="h-5 w-5" />
      default:
        return null
    }
  }

  const getPlanColor = (tier: string) => {
    switch (tier) {
      case "free":
        return "bg-gray-100 text-gray-800 border-gray-300"
      case "starter":
        return "bg-blue-100 text-blue-800 border-blue-300"
      case "growth":
        return "bg-purple-100 text-purple-800 border-purple-300"
      case "enterprise":
        return "bg-yellow-100 text-yellow-800 border-yellow-300"
      default:
        return "bg-gray-100 text-gray-800 border-gray-300"
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Billing & Subscription</h1>
          <p className="text-muted-foreground">Manage your subscription and monitor usage</p>
        </div>
        {isConnected && (
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <span className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
            Live Updates Active
          </Badge>
        )}
      </div>

      {/* Current Plan & Usage */}
      {subscription && usage && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Plan */}
          <Card className="lg:col-span-2 border-2 border-primary/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Current Plan</CardTitle>
                <Badge className={getPlanColor(subscription.plan.tier)}>
                  {getPlanIcon(subscription.plan.tier)}
                  <span className="ml-1 capitalize">{subscription.plan.tier}</span>
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <p className="text-4xl font-bold text-foreground">{subscription.plan.name}</p>
                  {subscription.plan.price > 0 && (
                    <p className="text-2xl text-muted-foreground mt-2">
                      ${subscription.plan.price}/{subscription.plan.currency}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <Badge variant={subscription.status === "active" ? "default" : "secondary"}>
                      {subscription.status}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Renewal Date</p>
                    <p className="font-medium">
                      {new Date(subscription.renewal_date).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {subscription.days_until_renewal} days remaining
                    </p>
                  </div>
                </div>

                {/* Plan Features */}
                <div>
                  <p className="text-sm font-semibold mb-2">Plan Features</p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>{subscription.plan.api_limit.toLocaleString()} API calls/month</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-green-500" />
                      <span>{subscription.plan.webhook_limit} webhook(s)</span>
                    </div>
                    {subscription.plan.has_analytics && (
                      <div className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="capitalize">{subscription.plan.analytics_level} analytics</span>
                      </div>
                    )}
                    {subscription.plan.has_priority_support && (
                      <div className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-500" />
                        <span>Priority support</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Usage Display */}
          <div>
            <UsageDisplay usage={usage} showAlert={true} />
          </div>
        </div>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {availablePlans.map((plan) => {
            const isCurrentPlan = subscription?.plan.tier === plan.tier
            
            return (
              <Card
                key={plan.id}
                className={`relative ${
                  isCurrentPlan
                    ? "border-2 border-primary bg-primary/5"
                    : "border border-border"
                }`}
              >
                {isCurrentPlan && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">Current Plan</Badge>
                  </div>
                )}
                
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    {getPlanIcon(plan.tier)}
                    <CardTitle className="text-xl">{plan.name}</CardTitle>
                  </div>
                  {plan.tier === "enterprise" ? (
                    <p className="text-2xl font-bold text-primary">Custom Pricing</p>
                  ) : plan.price > 0 ? (
                    <p className="text-3xl font-bold text-primary">
                      ${plan.price}
                      <span className="text-sm text-muted-foreground">/mo</span>
                    </p>
                  ) : (
                    <p className="text-3xl font-bold text-primary">Free</p>
                  )}
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <ul className="space-y-2">
                    <li className="text-sm flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{plan.api_limit.toLocaleString()} API calls/month</span>
                    </li>
                    <li className="text-sm flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{plan.webhook_limit} webhook(s)</span>
                    </li>
                    {plan.has_analytics && (
                      <li className="text-sm flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span className="capitalize">{plan.analytics_level} analytics</span>
                      </li>
                    )}
                    {plan.has_priority_support && (
                      <li className="text-sm flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span>Priority support</span>
                      </li>
                    )}
                    {plan.has_custom_branding && (
                      <li className="text-sm flex items-start gap-2">
                        <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span>Custom branding</span>
                      </li>
                    )}
                  </ul>
                  
                  <Button
                    className="w-full font-semibold"
                    disabled={isCurrentPlan}
                    onClick={() => handleUpgradeClick(plan)}
                    variant={isCurrentPlan ? "secondary" : "default"}
                    size="lg"
                  >
                    {isCurrentPlan 
                      ? "Current Plan" 
                      : plan.tier === "enterprise" 
                        ? "Contact Sales" 
                        : plan.price === 0 
                          ? "Downgrade" 
                          : "Upgrade"}
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Provider Selection Modal */}
      {selectedPlan && (
        <ProviderSelectionModal
          open={showProviderModal}
          onClose={() => setShowProviderModal(false)}
          onSelect={handleProviderSelect}
          planName={selectedPlan.name}
          amount={selectedPlan.price}
          currency={selectedPlan.currency}
        />
      )}
    </div>
  )
}
