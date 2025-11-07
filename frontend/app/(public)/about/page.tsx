"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Reveal } from "@/components/Reveal"
import Globe from "@/components/Globe"
import { Lightbulb, Handshake, Heart, Star, UsersRound, ShieldCheck, Globe as GlobeIcon, Code, Zap, Eye, GitBranch, Lock } from "lucide-react"

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-card to-background">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">About PayBridge</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              A unified API platform that simplifies how developers and businesses connect to Africa's growing fintech ecosystem
            </p>
          </Reveal>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <Reveal>
              <div className="space-y-6">
                <h2 className="text-3xl font-bold">🎯 Our Mission</h2>
                <p className="text-lg text-muted-foreground">
                  To connect Africa's fintech landscape into one open, developer-friendly ecosystem — enabling innovators to build financial products faster, smarter, and more securely.
                </p>
                <p className="text-muted-foreground">
                  PayBridge exists to remove the barriers that prevent African developers and startups from launching world-class financial services. We believe every developer should be able to build and deploy scalable fintech applications without worrying about inconsistent APIs, poor documentation, or fragmented integrations.
                </p>
                <Link href="/signup">
                  <Button className="mt-4">Get Started</Button>
                </Link>
              </div>
            </Reveal>
            <Reveal delayMs={100} className="h-full">
              <div className="bg-card/50 p-4 rounded-xl border border-border h-full overflow-hidden flex items-center justify-center">
                <Globe className="w-full" />
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-card/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <Reveal>
              <h2 className="text-3xl font-bold mb-4">💡 Our Core Values</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                The foundation of everything we do at PayBridge
              </p>
            </Reveal>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Simplicity",
                description: "Clean APIs, clear documentation, and developer-first design.",
                icon: Code
              },
              {
                title: "Reliability",
                description: "Every request matters. Our platform is built to be secure, stable, and production-ready.",
                icon: ShieldCheck
              },
              {
                title: "Transparency",
                description: "One dashboard, one billing system, full visibility into every call.",
                icon: Eye
              },
              {
                title: "Innovation",
                description: "We're enabling creators to build the future of fintech across Africa and beyond.",
                icon: Lightbulb
              },
              {
                title: "Community",
                description: "PayBridge is built for developers, by developers. We grow by empowering the community.",
                icon: UsersRound
              },
              {
                title: "Security",
                description: "Enterprise-grade security to protect your business and customers.",
                icon: Lock
              }
            ].map((value, index) => {
              const Icon = value.icon
              return (
                <Reveal key={index} delayMs={index * 50}>
                  <div className="bg-card/30 p-6 rounded-xl border border-border hover:border-primary transition-colors">
                    <Icon className="h-8 w-8 text-primary mb-4" />
                    <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                    <p className="text-muted-foreground">{value.description}</p>
                  </div>
                </Reveal>
              )
            })}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <Reveal className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Meet Our Leadership</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              The passionate team driving PayBridge's vision forward
            </p>
          </Reveal>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Alex Johnson",
                role: "CEO & Co-founder",
                bio: "Former fintech executive with 10+ years of experience in payment solutions."
              },
              {
                name: "Sarah Williams",
                role: "CTO & Co-founder",
                bio: "Technology leader specializing in scalable payment infrastructure."
              },
              {
                name: "Michael Chen",
                role: "Head of Product",
                bio: "Product strategist focused on creating seamless payment experiences."
              }
            ].map((member, index) => (
              <Reveal key={index} delayMs={index * 100}>
                <div className="text-center bg-card/50 p-8 rounded-xl border border-border">
                  <div className="w-32 h-32 mx-auto mb-6 rounded-full bg-muted flex items-center justify-center">
                    <span className="text-4xl font-semibold text-primary">
                      {member.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold">{member.name}</h3>
                  <p className="text-primary mb-4">{member.role}</p>
                  <p className="text-muted-foreground text-sm">{member.bio}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* What We Offer Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <Reveal>
              <h2 className="text-3xl font-bold mb-4">🚀 What PayBridge Offers</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Everything you need to build the future of African fintech
              </p>
            </Reveal>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            <Reveal>
              <div className="space-y-6">
                <h3 className="text-2xl font-semibold">Unified Fintech Integration</h3>
                <ul className="space-y-4 text-muted-foreground">
                  <li className="flex items-start">
                    <Zap className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Single API key to connect with multiple African fintech providers</span>
                  </li>
                  <li className="flex items-start">
                    <Zap className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Unified payment processing and KYC verification</span>
                  </li>
                  <li className="flex items-start">
                    <Zap className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Seamless transfers and balance management</span>
                  </li>
                </ul>
              </div>
            </Reveal>
            
            <Reveal delayMs={100}>
              <div className="space-y-6">
                <h3 className="text-2xl font-semibold">Developer Experience</h3>
                <ul className="space-y-4 text-muted-foreground">
                  <li className="flex items-start">
                    <Code className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Modern REST and GraphQL APIs with comprehensive documentation</span>
                  </li>
                  <li className="flex items-start">
                    <GitBranch className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Developer dashboard for monitoring and analytics</span>
                  </li>
                  <li className="flex items-start">
                    <GlobeIcon className="h-5 w-5 text-primary mr-2 mt-0.5 flex-shrink-0" />
                    <span>Real-time webhooks for transaction updates</span>
                  </li>
                </ul>
              </div>
            </Reveal>
          </div>
          
          <div className="mt-12 text-center">
            <Reveal>
              <p className="text-lg mb-6 max-w-3xl mx-auto">
                PayBridge is built on modern technologies including Next.js and Django, ensuring a robust, scalable, and production-ready platform for your fintech needs.
              </p>
              <Link href="/signup">
                <Button size="lg">Start Building Today</Button>
              </Link>
            </Reveal>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary to-secondary">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <Reveal>
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-primary-foreground">Ready to transform your payment infrastructure?</h2>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
              Join thousands of businesses that trust PayBridge for their payment processing needs.
            </p>
          </Reveal>
          <Reveal delayMs={200}>
            <Link href="/signup">
              <Button size="lg" className="bg-background text-foreground hover:bg-card">
                Get Started Today
              </Button>
            </Link>
          </Reveal>
        </div>
      </section>
    </main>
  )
}
