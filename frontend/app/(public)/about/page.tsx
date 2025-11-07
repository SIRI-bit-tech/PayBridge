"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Reveal } from "@/components/Reveal"

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-neutral-900 to-neutral-950">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">About PayBridge</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-neutral-300 max-w-3xl mx-auto">
              Empowering businesses across Africa with seamless payment solutions
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
                <h2 className="text-3xl font-bold">Our Mission</h2>
                <p className="text-lg text-neutral-300">
                  At PayBridge, we're on a mission to simplify payments across Africa by providing a unified 
                  platform that connects businesses with multiple payment providers through a single integration.
                </p>
                <p className="text-neutral-300">
                  We believe that businesses should focus on growth, not on managing multiple payment integrations. 
                  Our platform handles the complexity so you can focus on what matters most - your customers.
                </p>
                <Link href="/signup">
                  <Button className="mt-4">Get Started</Button>
                </Link>
              </div>
            </Reveal>
            <Reveal delayMs={100}>
              <div className="bg-neutral-900/50 p-8 rounded-xl border border-neutral-800 h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">🌍</div>
                  <p className="text-neutral-300">Connecting Africa through seamless payments</p>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-neutral-900/50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <Reveal>
              <h2 className="text-3xl font-bold mb-4">Our Core Values</h2>
              <p className="text-neutral-300 max-w-2xl mx-auto">
                These principles guide everything we do at PayBridge
              </p>
            </Reveal>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Innovation",
                description: "We constantly push boundaries to deliver cutting-edge payment solutions that drive business growth.",
                icon: "💡"
              },
              {
                title: "Integrity",
                description: "We build trust through transparency, security, and ethical business practices.",
                icon: "🤝"
              },
              {
                title: "Customer Focus",
                description: "Our customers are at the heart of everything we do. We listen, adapt, and deliver exceptional value.",
                icon: "❤️"
              },
              {
                title: "Excellence",
                description: "We strive for excellence in every aspect of our service, from technology to customer support.",
                icon: "🌟"
              },
              {
                title: "Collaboration",
                description: "We believe in the power of partnerships to create better solutions for our clients.",
                icon: "🌍"
              },
              {
                title: "Reliability",
                description: "Businesses depend on us, so we ensure our platform is always available and performing at its best.",
                icon: "🔒"
              }
            ].map((value, index) => (
              <Reveal key={index} delayMs={index * 50}>
                <div className="bg-neutral-800/30 p-6 rounded-xl border border-neutral-800 hover:border-blue-600 transition-colors">
                  <div className="text-3xl mb-4">{value.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                  <p className="text-neutral-300">{value.description}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <Reveal className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Meet Our Leadership</h2>
            <p className="text-neutral-300 max-w-2xl mx-auto">
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
                <div className="text-center bg-neutral-900/50 p-8 rounded-xl border border-neutral-800">
                  <div className="w-32 h-32 mx-auto mb-6 rounded-full bg-neutral-800 flex items-center justify-center text-4xl">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <h3 className="text-xl font-semibold">{member.name}</h3>
                  <p className="text-blue-400 mb-4">{member.role}</p>
                  <p className="text-neutral-300 text-sm">{member.bio}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <Reveal>
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to transform your payment infrastructure?</h2>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join thousands of businesses that trust PayBridge for their payment processing needs.
            </p>
          </Reveal>
          <Reveal delayMs={200}>
            <Link href="/signup">
              <Button size="lg" className="bg-white text-neutral-900 hover:bg-neutral-100">
                Get Started Today
              </Button>
            </Link>
          </Reveal>
        </div>
      </section>
    </main>
  )
}
