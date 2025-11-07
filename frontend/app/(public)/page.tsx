"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { PAYMENT_PROVIDERS } from "@/constants"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6 border-b border-border bg-card">
        <h1 className="text-2xl font-bold text-primary">PayBridge</h1>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="outline">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button>Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-24 text-center">
        <h2 className="text-5xl font-bold text-foreground mb-6">Pan-African Payment Aggregation</h2>
        <p className="text-xl text-muted-foreground mb-12">
          Integrate Paystack, Flutterwave, Stripe, and more with a single API. Expand your payment infrastructure across
          Africa.
        </p>
        <Link href="/signup">
          <Button size="lg" className="mb-20 bg-primary text-primary-foreground hover:bg-primary/90">
            Start Building
          </Button>
        </Link>
      </div>

      {/* Supported Providers */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h3 className="text-2xl font-bold text-foreground mb-8 text-center">Supported Providers</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {PAYMENT_PROVIDERS.map((provider) => (
            <div key={provider.id} className="bg-card rounded-lg p-6 text-center border border-border hover:border-primary transition-colors">
              <div className="text-4xl mb-3">{provider.icon}</div>
              <h4 className="text-card-foreground font-semibold">{provider.name}</h4>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h3 className="text-2xl font-bold text-foreground mb-8 text-center">Why PayBridge?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-card rounded-lg p-8 border border-border hover:border-primary transition-colors">
            <h4 className="text-primary text-lg font-bold mb-3">Unified API</h4>
            <p className="text-muted-foreground">Single integration for multiple payment providers across Africa</p>
          </div>
          <div className="bg-card rounded-lg p-8 border border-border hover:border-primary transition-colors">
            <h4 className="text-primary text-lg font-bold mb-3">Real-Time Analytics</h4>
            <p className="text-muted-foreground">Monitor transactions, revenue, and success rates in real-time</p>
          </div>
          <div className="bg-card rounded-lg p-8 border border-border hover:border-primary transition-colors">
            <h4 className="text-primary text-lg font-bold mb-3">Fraud Detection</h4>
            <p className="text-muted-foreground">ML-powered anomaly detection to protect your transactions</p>
          </div>
        </div>
      </div>
    </main>
  )
}