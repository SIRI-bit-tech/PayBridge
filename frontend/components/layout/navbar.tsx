"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/use-auth"

export function Navbar() {
  const router = useRouter()
  const { auth, clearAuth } = useAuth()

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    clearAuth()
    router.push("/login")
  }

  const displayName = auth?.user?.first_name || auth?.user?.email?.split('@')[0] || 'User'

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-8">
      <div>
        <p className="text-sm text-muted-foreground">Welcome,</p>
        <p className="font-semibold text-foreground">{displayName}</p>
      </div>
      <Button variant="outline" onClick={handleLogout}>
        Logout
      </Button>
    </header>
  )
}
