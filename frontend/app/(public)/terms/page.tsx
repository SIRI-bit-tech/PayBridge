"use client"

import { Button } from "@/components/ui/button"
import { Reveal } from "@/components/Reveal"

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-neutral-900 to-neutral-950">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Terms of Service</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-neutral-300">
              Last updated: November 6, 2025
            </p>
          </Reveal>
        </div>
      </section>

      {/* Terms Content */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="prose prose-invert max-w-none">
            <Reveal>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">1. Introduction</h2>
                <p className="text-neutral-300 mb-6">
                  Welcome to PayBridge. These Terms of Service ("Terms") govern your access to and use of our services, 
                  including our website, APIs, and any related services (collectively, the "Service").
                </p>
                <p className="text-neutral-300 mb-6">
                  By accessing or using our Service, you agree to be bound by these Terms and our Privacy Policy. 
                  If you are using our Service on behalf of an organization, you are agreeing to these Terms for 
                  that organization and representing that you have the authority to bind that organization to these Terms.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={50}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">2. Account Registration</h2>
                <p className="text-neutral-300 mb-4">
                  To use certain features of our Service, you must register for an account. You agree to provide accurate, 
                  current, and complete information during the registration process and to update such information to keep it 
                  accurate, current, and complete.
                </p>
                <p className="text-neutral-300">
                  You are responsible for maintaining the confidentiality of your account credentials and for all activities 
                  that occur under your account. You agree to notify us immediately of any unauthorized use of your account.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={100}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">3. Service Usage</h2>
                <p className="text-neutral-300 mb-4">
                  You agree to use our Service only for lawful purposes and in accordance with these Terms. You agree not to:
                </p>
                <ul className="list-disc pl-6 text-neutral-300 space-y-2 mb-4">
                  <li>Use our Service in any way that violates any applicable law or regulation</li>
                  <li>Engage in any fraudulent, deceptive, or illegal activity</li>
                  <li>Interfere with or disrupt the integrity or performance of our Service</li>
                  <li>Attempt to gain unauthorized access to our Service or related systems</li>
                  <li>Use our Service to transmit any viruses or malicious code</li>
                </ul>
              </div>
            </Reveal>

            <Reveal delayMs={150}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">4. Fees and Payments</h2>
                <p className="text-neutral-300 mb-4">
                  Certain features of our Service may be subject to fees. You agree to pay all applicable fees as described 
                  in our pricing plan or as otherwise agreed in writing. All fees are non-refundable except as required by law.
                </p>
                <p className="text-neutral-300">
                  We reserve the right to change our fees at any time. We will provide you with reasonable notice of any fee 
                  changes before they become effective.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={200}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">5. Intellectual Property</h2>
                <p className="text-neutral-300 mb-4">
                  Our Service and its entire contents, features, and functionality (including but not limited to all information, 
                  software, text, displays, images, and the design, selection, and arrangement thereof) are owned by PayBridge, 
                  its licensors, or other providers of such material and are protected by international copyright, trademark, patent, 
                  trade secret, and other intellectual property or proprietary rights laws.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={250}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">6. Limitation of Liability</h2>
                <p className="text-neutral-300 mb-4">
                  To the maximum extent permitted by law, in no event shall PayBridge, its affiliates, officers, directors, employees, 
                  agents, or licensors be liable for any indirect, punitive, incidental, special, consequential, or exemplary damages, 
                  including without limitation damages for loss of profits, goodwill, use, data, or other intangible losses, that result 
                  from the use of, or inability to use, our Service.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={300}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">7. Changes to Terms</h2>
                <p className="text-neutral-300">
                  We reserve the right to modify these Terms at any time. We will provide notice of any material changes to the Terms 
                  through our website or by other means. Your continued use of our Service after such notice constitutes your acceptance 
                  of the modified Terms.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={350}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">8. Contact Us</h2>
                <p className="text-neutral-300 mb-6">
                  If you have any questions about these Terms, please contact us at:
                </p>
                <Button variant="outline">
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
