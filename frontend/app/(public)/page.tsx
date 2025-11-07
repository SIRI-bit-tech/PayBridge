"use client"

import React, { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { PAYMENT_PROVIDERS } from "@/constants"

// Trusted companies using PayBridge
const TRUSTED_COMPANIES = [
  { name: "TechCorp Africa", description: "Processing $50M+ monthly across 15 African countries" },
  { name: "E-Commerce Hub", description: "Unified payments for 500+ merchants in West Africa" },
  { name: "FinTech Solutions", description: "Serving 2M+ users with seamless payment experiences" },
  { name: "Marketplace Pro", description: "Multi-provider integration handling 1M+ transactions/month" },
]

export default function LandingPage() {
  const [failedLogos, setFailedLogos] = useState<Set<string>>(new Set())
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

      {/* Trusted by Section */}
      <div className="max-w-6xl mx-auto px-6 py-16 bg-card/50 rounded-lg mb-12">
        <h3 className="text-2xl font-bold text-foreground mb-4 text-center">Trusted by Leading Companies</h3>
        <p className="text-muted-foreground text-center mb-12 max-w-2xl mx-auto">
          Big companies across Africa rely on PayBridge to power their payment infrastructure, processing millions of transactions and billions in revenue.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {TRUSTED_COMPANIES.map((company, index) => (
            <div key={index} className="bg-background rounded-lg p-6 border border-border hover:border-primary transition-colors">
              <h4 className="text-lg font-bold text-foreground mb-2">{company.name}</h4>
              <p className="text-muted-foreground text-sm">{company.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 text-muted-foreground">
            <span className="text-2xl font-bold text-primary">$500M+</span>
            <span>processed monthly</span>
          </div>
          <div className="mt-4 inline-flex items-center gap-2 text-muted-foreground">
            <span className="text-2xl font-bold text-primary">50+</span>
            <span>enterprise customers</span>
          </div>
        </div>
      </div>

      {/* Supported Providers */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h3 className="text-2xl font-bold text-foreground mb-8 text-center">Supported Providers</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {PAYMENT_PROVIDERS.map((provider) => {
            const showLogo = provider.logoUrl && !failedLogos.has(provider.id);
            
            return (
              <div key={provider.id} className="bg-card rounded-lg p-6 text-center border border-border hover:border-primary transition-colors">
                <div className="flex items-center justify-center mb-3 h-16">
                  {showLogo ? (
                    <img
                      src={provider.logoUrl}
                      alt={`${provider.name} logo`}
                      className="max-h-12 max-w-full object-contain"
                      onError={() => setFailedLogos(prev => new Set(prev).add(provider.id))}
                    />
                  ) : (
                    <span className="text-lg font-semibold text-muted-foreground">
                      {provider.name.charAt(0)}
                    </span>
                  )}
                </div>
                <h4 className="text-card-foreground font-semibold">{provider.name}</h4>
              </div>
            );
          })}
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