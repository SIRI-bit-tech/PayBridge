"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BILLING_PLANS } from "@/constants"
import { getSubscription } from "@/lib/api"
import type { Subscription } from "@/types"

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
        <h1 className="text-3xl font-bold text-white">Billing & Subscription</h1>
        <p className="text-neutral-400">Manage your subscription and billing</p>
      </div>

      {/* Current Plan */}
      {subscription && (
        <Card className="bg-neutral-800 border-neutral-700">
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-neutral-400 text-sm">Plan Name</p>
                <p className="text-2xl font-bold text-white capitalize">{subscription.plan}</p>
              </div>
              <div>
                <p className="text-neutral-400 text-sm">Status</p>
                <p className="text-lg font-semibold text-green-400 capitalize">{subscription.status}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-neutral-400 text-sm">Current Period Start</p>
                  <p className="text-white">{new Date(subscription.current_period_start).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-neutral-400 text-sm">Renewal Date</p>
                  <p className="text-white">{new Date(subscription.renewal_date).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(BILLING_PLANS).map(([key, plan]) => (
            <Card
              key={key}
              className={`border-neutral-700 ${subscription?.plan === key.toLowerCase() ? "bg-primary/10 border-primary" : "bg-neutral-800"}`}
            >
              <CardHeader>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                {plan.price && (
                  <p className="text-3xl font-bold text-primary mt-2">
                    ${plan.price}
                    <span className="text-sm text-neutral-400">/mo</span>
                  </p>
                )}
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="text-neutral-300 text-sm flex items-center gap-2">
                      <span className="text-primary">✓</span> {feature}
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
