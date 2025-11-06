"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { PAYMENT_PROVIDERS } from "@/constants"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900">
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6 border-b border-neutral-700">
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
        <h2 className="text-5xl font-bold text-white mb-6">Pan-African Payment Aggregation</h2>
        <p className="text-xl text-neutral-300 mb-12">
          Integrate Paystack, Flutterwave, Stripe, and more with a single API. Expand your payment infrastructure across
          Africa.
        </p>
        <Link href="/signup">
          <Button size="lg" className="mb-20">
            Start Building
          </Button>
        </Link>
      </div>

      {/* Supported Providers */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h3 className="text-2xl font-bold text-white mb-8 text-center">Supported Providers</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {PAYMENT_PROVIDERS.map((provider) => (
            <div key={provider.id} className="bg-neutral-800 rounded-lg p-6 text-center border border-neutral-700">
              <div className="text-4xl mb-3">{provider.icon}</div>
              <h4 className="text-white font-semibold">{provider.name}</h4>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h3 className="text-2xl font-bold text-white mb-8 text-center">Why PayBridge?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-neutral-800 rounded-lg p-8 border border-neutral-700">
            <h4 className="text-primary text-lg font-bold mb-3">Unified API</h4>
            <p className="text-neutral-300">Single integration for multiple payment providers across Africa</p>
          </div>
          <div className="bg-neutral-800 rounded-lg p-8 border border-neutral-700">
            <h4 className="text-primary text-lg font-bold mb-3">Real-Time Analytics</h4>
            <p className="text-neutral-300">Monitor transactions, revenue, and success rates in real-time</p>
          </div>
          <div className="bg-neutral-800 rounded-lg p-8 border border-neutral-700">
            <h4 className="text-primary text-lg font-bold mb-3">Fraud Detection</h4>
            <p className="text-neutral-300">ML-powered anomaly detection to protect your transactions</p>
          </div>
        </div>
      </div>
    </main>
  )
}
