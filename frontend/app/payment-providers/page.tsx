"use client"

import { useAuth } from "@/components/auth-provider"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Navbar } from "@/components/navbar"
import { Sidebar } from "@/components/sidebar"
import { apiCall } from "@/lib/api"

interface PaymentProvider {
  id: string
  provider: string
  is_live: boolean
  is_active: boolean
  created_at: string
}

const PROVIDERS = [
  { name: "paystack", label: "Paystack", icon: "🟦", docs: "https://paystack.com/docs" },
  { name: "flutterwave", label: "Flutterwave", icon: "🌊", docs: "https://developer.flutterwave.com/docs" },
  { name: "stripe", label: "Stripe", icon: "⬜", docs: "https://stripe.com/docs" },
  { name: "mono", label: "Mono", icon: "◆", docs: "https://mono.co/docs" },
  { name: "okra", label: "Okra", icon: "🌿", docs: "https://okra.ng/docs" },
  { name: "chapa", label: "Chapa", icon: "📱", docs: "https://chapa.co/docs" },
  { name: "lazerpay", label: "Lazerpay", icon: "⚡", docs: "https://lazerpay.com/docs" },
]

export default function PaymentProvidersPage() {
  const { auth } = useAuth()
  const router = useRouter()
  const [providers, setProviders] = useState<PaymentProvider[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [editingProvider, setEditingProvider] = useState<string | null>(null)
  const [formData, setFormData] = useState({ public_key: "", secret_key: "" })
  const [saving, setSaving] = useState(false)

  const isAuthenticated = Boolean(auth)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchProviders()
    }
  }, [isAuthenticated])

  const fetchProviders = async () => {
    setDataLoading(true)
    const response = await apiCall<{ results: PaymentProvider[] }>("/payment-providers/")
    if (response.data) {
      setProviders(response.data.results || [])
    }
    setDataLoading(false)
  }

  const handleSaveProvider = async (providerName: string) => {
    if (!formData.public_key || !formData.secret_key) {
      alert("Please fill in all fields")
      return
    }

    setSaving(true)
    const response = await apiCall("/payment-providers/", {
      method: "POST",
      body: JSON.stringify({
        provider: providerName,
        public_key: formData.public_key,
        secret_key: formData.secret_key,
      }),
    })

    if (response.status === 201 || response.status === 200) {
      await fetchProviders()
      setEditingProvider(null)
      setFormData({ public_key: "", secret_key: "" })
    }
    setSaving(false)
  }

  if (!isAuthenticated) {
    return (
      <>
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-muted-foreground">Redirecting...</div>
        </div>
      </>
    )
  }

  return (
    <>
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1">
          <div className="p-8">
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Payment Providers</h1>
                <p className="text-muted-foreground mt-2">Configure your payment provider credentials</p>
              </div>

              {dataLoading ? (
                <div className="text-center text-muted-foreground">Loading providers...</div>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  {PROVIDERS.map((provider) => {
                    const configured = providers.find((p) => p.provider === provider.name)
                    const isEditing = editingProvider === provider.name

                    return (
                      <div key={provider.name} className="bg-card/50 border border-border rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <span className="text-3xl">{provider.icon}</span>
                            <div>
                              <h3 className="font-semibold text-foreground">{provider.label}</h3>
                              {configured && (
                                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                                  Configured
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {isEditing ? (
                          <div className="space-y-3">
                            <input
                              type="text"
                              placeholder="Public Key"
                              value={formData.public_key}
                              onChange={(e) => setFormData({ ...formData, public_key: e.target.value })}
                              className="w-full px-3 py-2 bg-background border border-border rounded text-foreground placeholder-muted-foreground text-sm"
                            />
                            <input
                              type="password"
                              placeholder="Secret Key"
                              value={formData.secret_key}
                              onChange={(e) => setFormData({ ...formData, secret_key: e.target.value })}
                              className="w-full px-3 py-2 bg-background border border-border rounded text-foreground placeholder-muted-foreground text-sm"
                            />
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleSaveProvider(provider.name)}
                                disabled={saving}
                                className="flex-1 px-3 py-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded text-sm font-semibold transition-colors disabled:opacity-50"
                              >
                                {saving ? "Saving..." : "Save"}
                              </button>
                              <button
                                onClick={() => {
                                  setEditingProvider(null)
                                  setFormData({ public_key: "", secret_key: "" })
                                }}
                                className="flex-1 px-3 py-2 bg-muted hover:bg-muted/80 text-foreground rounded text-sm font-semibold transition-colors"
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-3">
                            <p className="text-sm text-muted-foreground">
                              {configured
                                ? "Your credentials are securely stored"
                                : "Add your API credentials to get started"}
                            </p>
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  setEditingProvider(provider.name)
                                  setFormData({ public_key: "", secret_key: "" })
                                }}
                                className="flex-1 px-3 py-2 bg-primary hover:bg-primary-dark text-white rounded text-sm font-semibold transition-colors"
                              >
                                {configured ? "Update" : "Add Credentials"}
                              </button>
                              <a
                                href={provider.docs}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-1 px-3 py-2 bg-neutral-700 hover:bg-neutral-600 text-white rounded text-sm font-semibold transition-colors text-center"
                              >
                                Docs
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
