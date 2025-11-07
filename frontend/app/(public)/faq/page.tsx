"use client"

import { Button } from "@/components/ui/button"
import { Reveal } from "@/components/Reveal"
import { ChevronDown } from "lucide-react"
import { useState } from "react"

const faqs = [
  {
    question: "What is PayBridge?",
    answer: "PayBridge is a pan-African payment aggregation platform that allows businesses to integrate multiple payment providers through a single API, making it easier to accept payments across Africa."
  },
  {
    question: "Which payment providers do you support?",
    answer: "We support all major African payment providers including Paystack, Flutterwave, and more. Our unified API makes it easy to connect with multiple providers simultaneously."
  },
  {
    question: "How do I get started with PayBridge?",
    answer: "Getting started is simple! Just sign up for an account, verify your business, and integrate our API into your platform. Our documentation provides step-by-step guides."
  },
  {
    question: "What are the fees for using PayBridge?",
    answer: "Our pricing is transparent and based on your transaction volume. We offer competitive rates that become more favorable as your business grows. Contact our sales team for a custom quote."
  },
  {
    question: "Is my transaction data secure?",
    answer: "Absolutely. We implement bank-level security measures including end-to-end encryption, PCI DSS compliance, and regular security audits to protect your data."
  },
  {
    question: "How long does it take to receive payouts?",
    answer: "Payout times vary by payment method and provider, but typically range from 1-3 business days. You can track all payouts in your dashboard."
  },
  {
    question: "Do you offer customer support?",
    answer: "Yes, we provide 24/7 customer support via email and live chat. Our dedicated support team is always ready to assist you with any questions or issues."
  },
  {
    question: "Can I use PayBridge for international payments?",
    answer: "Yes, our platform supports both local and international payments, allowing you to accept payments from customers around the world in multiple currencies."
  }
]

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-neutral-900 to-neutral-950">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Frequently Asked Questions</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-neutral-300 max-w-3xl mx-auto">
              Find answers to common questions about PayBridge and our services.
            </p>
          </Reveal>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <Reveal key={index} delayMs={index * 50}>
                <div className="bg-neutral-900/60 rounded-lg overflow-hidden border border-neutral-800">
                  <button
                    className="w-full flex items-center justify-between p-6 text-left"
                    onClick={() => toggleFAQ(index)}
                    aria-expanded={openIndex === index}
                    aria-controls={`faq-${index}`}
                  >
                    <h3 className="text-lg font-medium">{faq.question}</h3>
                    <ChevronDown 
                      className={`w-5 h-5 text-neutral-400 transition-transform duration-200 ${openIndex === index ? 'transform rotate-180' : ''}`} 
                    />
                  </button>
                  <div 
                    id={`faq-${index}`}
                    className={`px-6 pb-6 pt-0 transition-all duration-300 ${openIndex === index ? 'block' : 'hidden'}`}
                    aria-hidden={openIndex !== index}
                  >
                    <p className="text-neutral-300">{faq.answer}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>

          {/* CTA Section */}
          <div className="mt-16 text-center">
            <Reveal>
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-8 rounded-2xl">
                <h3 className="text-2xl font-bold mb-4">Still have questions?</h3>
                <p className="text-neutral-200 mb-6 max-w-2xl mx-auto">
                  Our support team is here to help you with any questions you might have about our platform.
                </p>
                <Button size="lg" className="bg-white text-neutral-900 hover:bg-neutral-100">
                  Contact Support
                </Button>
              </div>
            </Reveal>
          </div>
        </div>
      </section>
    </main>
  )
}
