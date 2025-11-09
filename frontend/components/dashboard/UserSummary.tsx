"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { getProfile } from "@/lib/api"
import { User, Building2, MapPin, CheckCircle2, XCircle } from "lucide-react"

interface UserProfile {
  first_name: string
  last_name: string
  email: string
  company_name: string
  country: string
  kyc_verified: boolean
  account_type: string
  created_at: string
}

export function UserSummary() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    const response = await getProfile()
    if (response.data) {
      setProfile(response.data as UserProfile)
    }
    setLoading(false)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Account Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Loading profile...</div>
        </CardContent>
      </Card>
    )
  }

  if (!profile) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Account Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Profile not found</div>
        </CardContent>
      </Card>
    )
  }

  const initials = `${profile.first_name[0]}${profile.last_name[0]}`.toUpperCase()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="bg-primary text-primary-foreground text-lg">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <h3 className="font-semibold text-lg">
              {profile.first_name} {profile.last_name}
            </h3>
            <p className="text-sm text-muted-foreground">{profile.email}</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Building2 className="h-4 w-4" />
              Company
            </div>
            <span className="font-medium">{profile.company_name || "Not set"}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MapPin className="h-4 w-4" />
              Country
            </div>
            <span className="font-medium">{profile.country}</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              Account Type
            </div>
            <Badge variant="outline" className="capitalize">
              {profile.account_type || "Standard"}
            </Badge>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              {profile.kyc_verified ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-yellow-500" />
              )}
              KYC Status
            </div>
            <Badge
              variant={profile.kyc_verified ? "default" : "secondary"}
              className={profile.kyc_verified ? "bg-green-500/10 text-green-500" : "bg-yellow-500/10 text-yellow-500"}
            >
              {profile.kyc_verified ? "Verified" : "Pending"}
            </Badge>
          </div>
        </div>

        {!profile.kyc_verified && (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            <p className="text-sm text-yellow-500">
              Complete KYC verification to unlock higher transaction limits
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
