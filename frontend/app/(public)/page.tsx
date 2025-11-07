"use client"

import React, { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import Globe from "@/components/Globe"
import { PAYMENT_PROVIDERS } from "@/constants"
import {
  BarChart3,
  Building2,
  Globe2,
  Link2,
  Lock,
  Server,
  ShieldCheck,
  Users,
  Zap,
} from "lucide-react"

const STRATEGIC_METRICS = [
  {
    label: "Monthly Volume",
    value: "$500M+",
    description: "Processed through PayBridge every month across 25 markets.",
    icon: BarChart3,
  },
  {
    label: "Partner Integrations",
    value: "60+",
    description: "Payment providers, banks, and mobile money networks connected.",
    icon: Link2,
  },
  {
    label: "Enterprise Clients",
    value: "200+",
    description: "High-growth companies scaling collections and payouts with us.",
    icon: Building2,
  },
  {
    label: "Reliability",
    value: "99.995%",
    description: "Measured uptime across our redundant switching infrastructure.",
    icon: Server,
  },
]

const SOLUTION_SECTIONS = [
  {
    title: "Unified Orchestration",
    description:
      "Aggregate cards, bank transfers, and mobile money in one contract. Route transactions dynamically based on cost and performance.",
    image:
      "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Realtime Intelligence",
    description:
      "Monitor conversion, latency, and declines in a single dashboard. Act on live insights with automated failover rules.",
    image:
      "https://images.unsplash.com/photo-1556157382-97eda2d62296?auto=format&fit=crop&w=900&q=80",
  },
  {
    title: "Embedded Payouts",
    description:
      "Disburse to vendors and riders in seconds with treasury reconciliation and automated compliance checks built-in.",
    image:
      "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=900&q=80",
  },
]

const CASE_STUDIES = [
  {
    name: "TechCorp Africa",
    title: "Scaled collections across 18 countries",
    quote:
      "PayBridge helped us unify fragmented payment providers into a single orchestration layer. We expanded into eight new markets in under six months.",
    image:
      "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    name: "ZenMarket",
    title: "Cut payment costs by 28%",
    quote:
      "Smart routing and automated retries reduced failed transactions dramatically. Our finance team finally has a single source of truth.",
    image:
      "https://images.unsplash.com/photo-1525182008055-f88b95ff7980?auto=format&fit=crop&w=1200&q=80",
  },
  {
    name: "Velocity Logistics",
    title: "Same-day payouts to 50k partners",
    quote:
      "Disbursements that once took days now land instantly, mapped to local compliance requirements. PayBridge is our financial nerve centre.",
    image:
      "https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=1200&q=80",
  },
]

const COMPLIANCE_BADGES = [
  { title: "PCI-DSS Level 1", description: "Audited infrastructure with tokenised card vaults", icon: ShieldCheck },
  { title: "ISO 27001", description: "Enterprise-grade information security controls", icon: Lock },
  { title: "RegTech Monitoring", description: "Continuous AML / CFT screening across providers", icon: Users },
  { title: "24/7 NOC", description: "Global operations teams monitoring uptime in real-time", icon: Globe2 },
]

export default function LandingPage() {
  const [failedLogos, setFailedLogos] = useState<Set<string>>(new Set())
  return (
    <main className="min-h-screen bg-background relative overflow-hidden">
      {/* Oversized Globe background spanning across both sides and deeper down the page */}
      <div aria-hidden className="pointer-events-none absolute top-0 left-1/2 -z-10 transform -translate-x-1/2">
        <div className="opacity-40" style={{ width: "160vw", maxWidth: "160vw", height: 1500 }}>
          <Globe className="w-full" height={1500} />
        </div>
      </div>
      {/* Navigation */}
      <nav className="flex items-center justify-between p-6 border-b border-border bg-card">
        <h1 className="text-2xl font-bold text-primary">PayBridge</h1>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="outline">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button
              variant="outline"
              className="bg-transparent text-foreground hover:bg-primary/10 hover:text-primary hover:border-primary transition-colors"
            >
              Get Started
            </Button>
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
          <Button
            size="lg"
            variant="outline"
            className="mb-20 bg-transparent text-foreground hover:bg-primary/10 hover:text-primary hover:border-primary transition-colors"
          >
            Start Building
          </Button>
        </Link>
      </div>

      {/* Strategic Metrics */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h3 className="text-3xl font-bold text-foreground">Enterprise-Grade Payments at Continental Scale</h3>
          <p className="mt-4 text-muted-foreground">
            Built for high-velocity businesses moving billions of dollars across Africa. PayBridge connects the full payment
            value chain—collections, payouts, treasury, and compliance.
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-4">
          {STRATEGIC_METRICS.map((metric) => {
            const Icon = metric.icon
            return (
              <div
                key={metric.label}
                className="rounded-2xl border border-border bg-card/60 p-6 shadow-sm backdrop-blur transition hover:border-primary hover:shadow-lg"
              >
                <Icon className="mb-4 h-8 w-8 text-primary" />
                <p className="text-3xl font-bold text-foreground">{metric.value}</p>
                <p className="mt-1 text-sm font-medium uppercase tracking-wide text-muted-foreground">{metric.label}</p>
                <p className="mt-4 text-sm text-muted-foreground">{metric.description}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Platform Overview */}
      <section className="bg-card/50 py-16">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 md:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <h3 className="text-3xl font-bold text-foreground">A single orchestration layer for Africa&apos;s payment rails</h3>
            <p className="text-lg text-muted-foreground">
              Our infrastructure abstracts fragmented providers into a unified platform. Manage local payment schemes, mobile
              wallets, and global card networks through one contract and dashboard.
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                { icon: Zap, title: "Smart routing", text: "ML-powered decisions optimise approval rates and fees." },
                { icon: ShieldCheck, title: "Active monitoring", text: "24/7 NOC with instant alerts and automated failovers." },
                { icon: Server, title: "Multi-region redundancy", text: "Resilient architecture across Lagos, Nairobi, and Cape Town." },
                { icon: Users, title: "Unified insights", text: "Finance, ops, and engineering share the same live data." },
              ].map((item) => {
                const Icon = item.icon
                return (
                  <div key={item.title} className="flex gap-3 rounded-xl border border-border bg-background/70 p-4">
                    <Icon className="h-6 w-6 text-primary" />
                    <div>
                      <p className="font-semibold text-foreground">{item.title}</p>
                      <p className="text-sm text-muted-foreground">{item.text}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          <div className="relative overflow-hidden rounded-3xl border border-border shadow-xl">
            <img
              src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=80"
              alt="PayBridge platform overview"
              className="h-full w-full object-cover"
              loading="lazy"
            />
            <div className="absolute bottom-6 right-6 rounded-xl bg-background/90 p-4 shadow">
              <p className="text-xs font-semibold uppercase tracking-wide text-primary">Live Insights</p>
              <p className="text-lg font-bold text-foreground">Decline rate down 32% this week</p>
              <p className="text-xs text-muted-foreground">Automated routing to best-performing provider</p>
            </div>
          </div>
        </div>
      </section>

      {/* Solutions */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h3 className="text-3xl font-bold text-foreground">Solutions for every payment workflow</h3>
          <p className="mt-4 text-muted-foreground">
            Modular capabilities that slot into your stack—whether you&apos;re collecting, disbursing, or reconciling at scale.
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-3">
          {SOLUTION_SECTIONS.map((solution) => (
            <div
              key={solution.title}
              className="flex flex-col overflow-hidden rounded-3xl border border-border bg-card/70 shadow-sm transition hover:-translate-y-1 hover:border-primary hover:shadow-lg"
            >
              <div className="h-48 w-full overflow-hidden">
                <img
                  src={solution.image}
                  alt={solution.title}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
              </div>
              <div className="flex flex-1 flex-col gap-4 p-6">
                <h4 className="text-xl font-semibold text-foreground">{solution.title}</h4>
                <p className="text-sm text-muted-foreground">{solution.description}</p>
                <div className="mt-auto pt-4">
                  <Link href="/contact" className="text-sm font-medium text-primary hover:underline">
                    Talk to solutions engineering →
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Case Studies */}
      <section className="bg-card/60 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-foreground">Trusted by Africa&apos;s fastest-growing enterprises</h3>
            <p className="mt-4 text-muted-foreground">
              Stories from product, finance, and operations leaders using PayBridge as their payment backbone.
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {CASE_STUDIES.map((customer) => (
              <article
                key={customer.name}
                className="flex h-full flex-col overflow-hidden rounded-3xl border border-border bg-background/80 p-6 shadow-sm backdrop-blur"
              >
                <div className="relative mb-4 h-40 w-full overflow-hidden rounded-2xl">
                  <img
                    src={customer.image}
                    alt={`${customer.name} team`}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                </div>
                <h4 className="text-xl font-semibold text-foreground">{customer.title}</h4>
                <p className="mt-3 text-sm text-muted-foreground">“{customer.quote}”</p>
                <p className="mt-6 text-sm font-semibold text-primary">{customer.name}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Global Reach */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid gap-10 md:grid-cols-[0.9fr_1.1fr] items-center">
          <div className="space-y-6">
            <h3 className="text-3xl font-bold text-foreground">Global-grade infrastructure, local market expertise</h3>
            <p className="text-muted-foreground">
              We maintain on-the-ground partnerships with regulators and financial institutions across Africa. Our network
              of data centres and banking partners ensures resilience and regulatory compliance.
            </p>
            <ul className="space-y-4">
              {["Direct integrations with central switches in 8 countries", "Treasury services with top-tier African banks", "Dedicated success teams in Lagos, Nairobi, Johannesburg, and Cairo"].map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <span className="mt-1 inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary/10">
                    <Globe2 className="h-4 w-4 text-primary" />
                  </span>
                  <span className="text-sm text-muted-foreground">{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="overflow-hidden rounded-3xl border border-border shadow-lg">
            <img
              src="https://images.unsplash.com/photo-1473163928189-364b2c4e1135?auto=format&fit=crop&w=1400&q=80"
              alt="Network map across Africa"
              className="w-full object-cover"
              loading="lazy"
            />
          </div>
        </div>
      </section>

      {/* Ecosystem Partners */}
      <section className="bg-card/50 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-10">
            <h3 className="text-3xl font-bold text-foreground">Connected to the payment ecosystem you rely on</h3>
            <p className="mt-4 text-muted-foreground">
              Seamlessly plug into your existing providers while unlocking new markets through PayBridge.
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-3 md:grid-cols-4">
            {PAYMENT_PROVIDERS.map((provider) => {
              const showLogo = provider.logoUrl && !failedLogos.has(provider.id)
              return (
                <div
                  key={provider.id}
                  className="flex h-28 flex-col items-center justify-center rounded-2xl border border-border bg-background/70 p-4 text-center shadow-sm"
                >
                  {showLogo ? (
                    <img
                      src={provider.logoUrl}
                      alt={`${provider.name} logo`}
                      className="max-h-12 max-w-full object-contain"
                      loading="lazy"
                      onError={() => setFailedLogos((prev) => new Set(prev).add(provider.id))}
                    />
                  ) : (
                    <span className="text-lg font-semibold text-muted-foreground">{provider.name}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Compliance & Security */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid gap-10 md:grid-cols-2">
          <div>
            <h3 className="text-3xl font-bold text-foreground">Security and compliance designed for financial institutions</h3>
            <p className="mt-4 text-muted-foreground">
              From tokenised card vaults to continuous AML screening, PayBridge is architected to meet the stringent demands
              of regulated enterprises.
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2">
            {COMPLIANCE_BADGES.map((badge) => {
              const Icon = badge.icon
              return (
                <div key={badge.title} className="rounded-2xl border border-border bg-card/60 p-5">
                  <Icon className="h-7 w-7 text-primary" />
                  <p className="mt-4 text-lg font-semibold text-foreground">{badge.title}</p>
                  <p className="mt-2 text-sm text-muted-foreground">{badge.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>
    </main>
  )
}