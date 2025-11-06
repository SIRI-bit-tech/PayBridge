"use client"

import Link from "next/link"
import { useAuth } from "@/components/auth-provider"
import { useRouter } from "next/navigation"

export function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <nav className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 font-bold text-lg">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">
                PB
              </div>
              <span className="hidden sm:inline">PayBridge</span>
            </Link>
            {isAuthenticated && (
              <div className="hidden md:flex gap-6">
                <Link href="/dashboard" className="text-sm hover:text-primary transition-colors">
                  Dashboard
                </Link>
                <Link href="/api-keys" className="text-sm hover:text-primary transition-colors">
                  API Keys
                </Link>
                <Link href="/transactions" className="text-sm hover:text-primary transition-colors">
                  Transactions
                </Link>
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/settings" className="text-sm hover:text-primary transition-colors">
                  Settings
                </Link>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 transition-colors text-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-sm hover:text-primary transition-colors">
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-dark text-white transition-colors text-sm"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
