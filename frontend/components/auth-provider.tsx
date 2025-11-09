"use client"

import type React from "react"
import { createContext, useContext, useState, useCallback, useEffect } from "react"
import type { User } from "@/types"

interface AuthContextType {
  auth: { token: string; user: User } | null
  setAuth: (auth: { token: string; user: User } | null) => void
  clearAuth: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuthState] = useState<{ token: string; user: User } | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize auth from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // Try to get user info from localStorage or fetch it
      const userStr = localStorage.getItem('user_info')
      if (userStr) {
        try {
          const user = JSON.parse(userStr)
          setAuthState({ token, user })
        } catch (e) {
          console.error('Failed to parse user info:', e)
        }
      }
    }
    setIsInitialized(true)
  }, [])

  const setAuth = useCallback((auth: { token: string; user: User } | null) => {
    setAuthState(auth)
    if (auth) {
      localStorage.setItem('user_info', JSON.stringify(auth.user))
    } else {
      localStorage.removeItem('user_info')
    }
  }, [])

  const clearAuth = useCallback(() => {
    setAuthState(null)
    localStorage.removeItem('user_info')
  }, [])

  // Don't render children until auth is initialized
  if (!isInitialized) {
    return null
  }

  return <AuthContext.Provider value={{ auth, setAuth, clearAuth }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
