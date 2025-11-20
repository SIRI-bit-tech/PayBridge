"use client"

import { useEffect, useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, Building2, CreditCard } from "lucide-react"
import { toast } from "sonner"
import { 
  getBusinessProfile, 
  updateBusinessProfile, 
  getProviderConfigs,
  createProviderConfig,
  deleteProviderConfig,
  validateProviderConfig,
  setPrimaryProvider,
  toggleProviderMode
} from "@/lib/api"
import type { BusinessProfile, PaymentProviderConfig } from "@/types"
import { useSocket } from "@/hooks/useSocket"
import { BusinessProfileForm } from "@/components/settings/BusinessProfileForm"
import { ProviderCard } from "@/components/settings/ProviderCard"
import { AddProviderDialog } from "@/components/settings/AddProviderDialog"

export default function SettingsPage() {
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState<BusinessProfile | null>(null)
  const [providers, setProviders] = useState<PaymentProviderConfig[]>([])
  
  const { socket, isConnected } = useSocket()
  
  useEffect(() => {
    loadData()
  }, [])
  
  // Socket.IO real-time updates
  useEffect(() => {
    if (!socket) return
    
    socket.emit("join_settings")
    
    socket.on("settings:profile_updated", (data: BusinessProfile) => {
      console.log("Profile updated via Socket.IO:", data)
      setProfile(data)
      toast.success("Profile updated in real-time")
    })
    
    socket.on("settings:provider_added", (data: PaymentProviderConfig) => {
      console.log("Provider added via Socket.IO:", data)
      setProviders(prev => [...prev, data])
      toast.success(`${data.provider} provider added`)
    })
    
    socket.on("settings:provider_updated", (data: PaymentProviderConfig) => {
      console.log("Provider updated via Socket.IO:", data)
      setProviders(prev => prev.map(p => p.id === data.id ? data : p))
      toast.success(`${data.provider} provider updated`)
    })
    
    socket.on("settings:provider_deleted", (data: { id: string; provider: string }) => {
      console.log("Provider deleted via Socket.IO:", data)
      setProviders(prev => prev.filter(p => p.id !== data.id))
      toast.success(`${data.provider} provider removed`)
    })
    
    socket.on("settings:provider_mode_changed", (data: PaymentProviderConfig) => {
      console.log("Provider mode changed via Socket.IO:", data)
      setProviders(prev => prev.map(p => p.id === data.id ? data : p))
      toast.success(`${data.provider} switched to ${data.mode} mode`)
    })
    
    return () => {
      socket.off("settings:profile_updated")
      socket.off("settings:provider_added")
      socket.off("settings:provider_updated")
      socket.off("settings:provider_deleted")
      socket.off("settings:provider_mode_changed")
      socket.emit("leave_settings")
    }
  }, [socket])
  
  const loadData = async () => {
    setLoading(true)
    try {
      const [profileRes, providersRes] = await Promise.all([
        getBusinessProfile(),
        getProviderConfigs(),
      ])
      
      if (profileRes && profileRes.data) {
        const profileData = Array.isArray(profileRes.data) ? profileRes.data[0] : profileRes.data
        setProfile(profileData)
      }
      
      if (providersRes && providersRes.data) {
        setProviders(providersRes.data as PaymentProviderConfig[])
      }
    } catch (error) {
      console.error("Error loading settings:", error)
      toast.error("Failed to load settings")
    } finally {
      setLoading(false)
    }
  }
  
  const handleUpdateProfile = async (data: Partial<BusinessProfile>) => {
    try {
      const response = await updateBusinessProfile(data)
      if (response && response.data) {
        toast.success("Profile updated successfully")
      } else {
        toast.error("Failed to update profile")
      }
    } catch (error) {
      console.error("Error updating profile:", error)
      toast.error("Failed to update profile")
    }
  }
  
  const handleAddProvider = async (data: any) => {
    try {
      const response = await createProviderConfig({
        ...data,
        is_active: true,
      })
      
      if (response && response.data) {
        toast.success("Provider added successfully")
        
        if ((response as any).validated === false) {
          toast.error((response as any).validation_error || "Provider credentials validation failed")
        }
      } else {
        toast.error("Failed to add provider")
      }
    } catch (error) {
      console.error("Error adding provider:", error)
      toast.error("Failed to add provider")
    }
  }
  
  const handleValidateProvider = async (id: string) => {
    try {
      const response = await validateProviderConfig(id)
      if (response && response.data) {
        if ((response.data as any).validated) {
          toast.success("Provider credentials validated successfully")
        } else {
          toast.error((response.data as any).error || "Validation failed")
        }
      }
    } catch (error) {
      console.error("Error validating provider:", error)
      toast.error("Failed to validate provider")
    }
  }
  
  const handleToggleMode = async (id: string) => {
    try {
      const response = await toggleProviderMode(id)
      if (response && response.data) {
        toast.success("Mode toggled successfully")
      }
    } catch (error) {
      console.error("Error toggling mode:", error)
      toast.error("Failed to toggle mode")
    }
  }
  
  const handleSetPrimary = async (id: string) => {
    try {
      const response = await setPrimaryProvider(id)
      if (response && response.data) {
        toast.success("Primary provider updated")
      }
    } catch (error) {
      console.error("Error setting primary:", error)
      toast.error("Failed to set primary provider")
    }
  }
  
  const handleDeleteProvider = async (id: string) => {
    const provider = providers.find(p => p.id === id)
    if (!confirm(`Are you sure you want to delete ${provider?.provider}?`)) return
    
    try {
      const response = await deleteProviderConfig(id)
      if (response && (response.status === 204 || response.status === 200)) {
        toast.success("Provider deleted successfully")
      }
    } catch (error) {
      console.error("Error deleting provider:", error)
      toast.error("Failed to delete provider")
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }
  
  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Manage your business profile and payment integrations</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-sm text-muted-foreground">
            {isConnected ? "Live" : "Disconnected"}
          </span>
        </div>
      </div>
      
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <Building2 className="w-4 h-4" />
            Business Profile
          </TabsTrigger>
          <TabsTrigger value="providers" className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Payment Providers
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="profile" className="space-y-6">
          <BusinessProfileForm profile={profile} onSave={handleUpdateProfile} />
        </TabsContent>
        
        <TabsContent value="providers" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold">Payment Providers</h2>
              <p className="text-sm text-muted-foreground">
                Connect and manage your payment provider integrations
              </p>
            </div>
            <AddProviderDialog onAdd={handleAddProvider} />
          </div>
          
          {providers.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed rounded-lg">
              <CreditCard className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No providers configured</h3>
              <p className="text-muted-foreground mb-4">
                Add your first payment provider to start accepting payments
              </p>
              <AddProviderDialog onAdd={handleAddProvider} />
            </div>
          ) : (
            <div className="grid gap-4">
              {providers.map((provider) => (
                <ProviderCard
                  key={provider.id}
                  provider={provider}
                  onValidate={handleValidateProvider}
                  onToggleMode={handleToggleMode}
                  onSetPrimary={handleSetPrimary}
                  onDelete={handleDeleteProvider}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
