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

  return (
    <header className="h-16 bg-neutral-800 border-b border-neutral-700 flex items-center justify-between px-8">
      <div>
        <p className="text-sm text-neutral-400">Welcome,</p>
        <p className="font-semibold text-white">{auth?.user?.email}</p>
      </div>
      <Button variant="outline" onClick={handleLogout}>
        Logout
      </Button>
    </header>
  )
}
