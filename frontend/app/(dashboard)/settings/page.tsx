"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getProfile, updateProfile, getPaymentProviders, createPaymentProvider } from "@/lib/api"
import { PAYMENT_PROVIDERS } from "@/constants"
import type { User, PaymentProvider } from "@/types"

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [providers, setProviders] = useState<PaymentProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  const [formData, setFormData] = useState({
    company_name: "",
    country: "NG",
    phone_number: "",
    business_type: "",
  })

  const [newProvider, setNewProvider] = useState({
    provider: "",
    public_key: "",
    secret_key: "",
    is_live: false,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    const [userRes, providersRes] = await Promise.all([getProfile(), getPaymentProviders()])

    if (userRes.data) {
      const userData = userRes.data as User
      setUser(userData)
      setFormData({
        company_name: userData.company_name,
        country: userData.country,
        phone_number: userData.phone_number || "",
        business_type: userData.business_type || "",
      })
    }

    if (providersRes.data) {
      setProviders(providersRes.data as PaymentProvider[])
    }

    setLoading(false)
  }

  const handleUpdateProfile = async () => {
    setUpdating(true)
    const response = await updateProfile(formData)
    if (response.data) {
      setUser(response.data as User)
    }
    setUpdating(false)
  }

  const handleAddProvider = async () => {
    if (!newProvider.provider || !newProvider.public_key || !newProvider.secret_key) return

    const response = await createPaymentProvider(newProvider)
    if (response.data) {
      setProviders([...providers, response.data as PaymentProvider])
      setNewProvider({ provider: "", public_key: "", secret_key: "", is_live: false })
    }
  }

  if (loading) return <div className="p-8 text-foreground">Loading...</div>

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground">Manage your profile and integrations</p>
      </div>

      {/* Profile Settings */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <CardDescription>Update your business details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Company Name"
            value={formData.company_name}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            className="bg-background border-border"
          />
          <Input
            placeholder="Phone Number"
            value={formData.phone_number}
            onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
            className="bg-background border-border"
          />
          <Input
            placeholder="Business Type"
            value={formData.business_type}
            onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
            className="bg-background border-border"
          />
          <Select value={formData.country} onValueChange={(value) => setFormData({ ...formData, country: value })}>
            <SelectTrigger className="bg-background border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NG">Nigeria</SelectItem>
              <SelectItem value="GH">Ghana</SelectItem>
              <SelectItem value="KE">Kenya</SelectItem>
              <SelectItem value="UG">Uganda</SelectItem>
              <SelectItem value="ZA">South Africa</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleUpdateProfile} disabled={updating}>
            {updating ? "Updating..." : "Update Profile"}
          </Button>
        </CardContent>
      </Card>

      {/* Payment Providers */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Payment Providers</CardTitle>
          <CardDescription>Configure your payment provider credentials</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Add Provider */}
          <div className="border-t border-border pt-6">
            <h3 className="font-semibold text-foreground mb-4">Add Provider Credentials</h3>
            <div className="space-y-4">
              <Select
                value={newProvider.provider}
                onValueChange={(value) => setNewProvider({ ...newProvider, provider: value })}
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Select Provider" />
                </SelectTrigger>
                <SelectContent>
                  {PAYMENT_PROVIDERS.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                placeholder="Public Key"
                value={newProvider.public_key}
                onChange={(e) => setNewProvider({ ...newProvider, public_key: e.target.value })}
                className="bg-background border-border"
              />
              <Input
                placeholder="Secret Key"
                type="password"
                value={newProvider.secret_key}
                onChange={(e) => setNewProvider({ ...newProvider, secret_key: e.target.value })}
                className="bg-background border-border"
              />
              <label className="flex items-center gap-2 text-muted-foreground cursor-pointer">
                <input
                  type="checkbox"
                  checked={newProvider.is_live}
                  onChange={(e) => setNewProvider({ ...newProvider, is_live: e.target.checked })}
                  className="rounded"
                />
                <span>Live Mode</span>
              </label>
              <Button onClick={handleAddProvider} disabled={!newProvider.provider}>
                Add Provider
              </Button>
            </div>
          </div>

          {/* Active Providers */}
          {providers.length > 0 && (
            <div className="border-t border-border pt-6">
              <h3 className="font-semibold text-foreground mb-4">Active Providers</h3>
              <div className="space-y-3">
                {providers.map((provider) => (
                  <div key={provider.id} className="bg-muted rounded p-4 border border-border">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-foreground capitalize">{provider.provider}</p>
                        <p className="text-sm text-muted-foreground">{provider.is_live ? "Live Mode" : "Test Mode"}</p>
                      </div>
                      <div
                        className={`px-3 py-1 rounded text-xs font-semibold ${provider.is_active ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}`}
                      >
                        {provider.is_active ? "Active" : "Inactive"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
