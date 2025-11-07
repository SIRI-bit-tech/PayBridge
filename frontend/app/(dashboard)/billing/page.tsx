"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BILLING_PLANS } from "@/constants"
import { getSubscription } from "@/lib/api"
import type { Subscription } from "@/types"
import { Check } from "lucide-react"

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSubscription()
  }, [])

  const fetchSubscription = async () => {
    const response = await getSubscription()
    if (response.data) {
      setSubscription(response.data as Subscription)
    }
    setLoading(false)
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Billing & Subscription</h1>
        <p className="text-muted-foreground">Manage your subscription and billing</p>
      </div>

      {/* Current Plan */}
      {subscription && (
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-muted-foreground text-sm">Plan Name</p>
                <p className="text-2xl font-bold text-foreground capitalize">{subscription.plan}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-sm">Status</p>
                <p className="text-lg font-semibold text-green-500 capitalize">{subscription.status}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-muted-foreground text-sm">Current Period Start</p>
                  <p className="text-foreground">{new Date(subscription.current_period_start).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-sm">Renewal Date</p>
                  <p className="text-foreground">{new Date(subscription.renewal_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(BILLING_PLANS).map(([key, plan]) => (
            <Card
              key={key}
              className={`border ${subscription?.plan === key.toLowerCase() ? "border-primary bg-primary/10" : "border-border bg-card"}`}
            >
              <CardHeader>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                {plan.price && (
                  <p className="text-3xl font-bold text-primary mt-2">
                    ${plan.price}
                    <span className="text-sm text-muted-foreground">/mo</span>
                  </p>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="text-muted-foreground text-sm flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" /> {feature}
                    </li>
                  ))}
                </ul>
                <Button className="w-full" disabled={subscription?.plan === key.toLowerCase()}>
                  {subscription?.plan === key.toLowerCase() ? "Current Plan" : "Upgrade"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
