"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { login, requestPasswordReset } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"
import { toast } from "sonner"

export default function LoginPage() {
  const router = useRouter()
  const { setAuth } = useAuth()
  const [identifier, setIdentifier] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showResetPassword, setShowResetPassword] = useState(false)
  const [resetEmail, setResetEmail] = useState("")
  const [isResetting, setIsResetting] = useState(false)
  const [resetSent, setResetSent] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      // Determine if identifier is email or phone
      const credentials = {
        [identifier.includes('@') ? 'email' : 'phone_number']: identifier,
        password,
        remember_me: rememberMe
      }

      const response = await login(credentials)

      if (response.error) {
        setError(response.error)
      } else {
        const { access, user } = response.data as any
        // The token is now in an HTTP-only cookie, we don't need to store it in localStorage
        setAuth({ token: access, user })
        router.push("/dashboard")
      }
    } catch (error) {
      setError("An error occurred during login. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!resetEmail) {
      setError("Please enter your email or phone number")
      return
    }

    setIsResetting(true)
    setError("")

    try {
      const response = await requestPasswordReset(resetEmail)
      if (response.error) {
        setError(response.error)
      } else {
        setResetSent(true)
        toast.success("Password reset email sent. Please check your inbox.")
      }
    } catch (error) {
      setError("Failed to send reset email. Please try again.")
    } finally {
      setIsResetting(false)
    }
  }

  if (showResetPassword) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-card to-background px-4">
        <Card className="w-full max-w-md bg-card border-border">
          <CardHeader>
            <CardTitle className="text-2xl">Reset Password</CardTitle>
            <CardDescription>Enter your email or phone to receive a reset link</CardDescription>
          </CardHeader>
          <form onSubmit={handlePasswordReset}>
            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">
                  {error}
                </div>
              )}
              {resetSent ? (
                <div className="p-3 text-sm text-green-600 bg-green-50 rounded-md">
                  If an account exists with that email or phone, you'll receive a password reset link.
                </div>
              ) : (
                <>
                  <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-medium">
                      Email or Phone
                    </label>
                    <Input
                      id="reset-email"
                      type="text"
                      placeholder="Enter your email or number"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={isResetting}>
                    {isResetting ? "Sending..." : "Send Reset Link"}
                  </Button>
                </>
              )}
            </CardContent>
          </form>
          <CardFooter className="justify-center">
            <Button 
              variant="ghost" 
              onClick={() => setShowResetPassword(false)}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Back to login
            </Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-card to-background px-4">
      <Card className="w-full max-w-md bg-card border-border">
        <CardHeader>
          <CardTitle className="text-2xl">Sign In</CardTitle>
          <CardDescription>Access your PayBridge dashboard</CardDescription>
        </CardHeader>
        <form onSubmit={handleLogin}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <label htmlFor="identifier" className="text-sm font-medium">
                Email or Phone
              </label>
              <Input
                id="identifier"
                type="text"
                placeholder="name@example.com or +1234567890"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowResetPassword(true)}
                  className="text-sm text-primary hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="remember" 
                checked={rememberMe}
                onCheckedChange={(checked) => setRememberMe(!!checked)}
              />
              <label
                htmlFor="remember"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Remember me
              </label>
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </CardContent>
        </form>
        <CardFooter className="flex-col space-y-4">
          <div className="text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
