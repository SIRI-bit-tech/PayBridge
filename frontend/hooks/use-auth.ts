"use client"

import { useContext } from "react"

// Re-export the context for hook usage
const AuthContextValue = (global as any).AuthContext

export const useAuth = () => {
  const context = useContext(AuthContextValue)
  if (!context) {
    return { auth: null, setAuth: () => {}, clearAuth: () => {} }
  }
  return context
}
