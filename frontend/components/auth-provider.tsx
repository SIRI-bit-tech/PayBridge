"use client"

import type React from "react"
import { createContext, useContext, useState, useCallback } from "react"
import type { User } from "@/types"

interface AuthContextType {
  auth: { token: string; user: User } | null
  setAuth: (auth: { token: string; user: User } | null) => void
  clearAuth: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuthState] = useState<{ token: string; user: User } | null>(null)

  const setAuth = useCallback((auth: { token: string; user: User } | null) => {
    setAuthState(auth)
  }, [])

  const clearAuth = useCallback(() => {
    setAuthState(null)
  }, [])

  return <AuthContext.Provider value={{ auth, setAuth, clearAuth }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}
