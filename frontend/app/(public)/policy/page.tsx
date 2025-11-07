"use client"

import { Button } from "@/components/ui/button"
import { Reveal } from "@/components/Reveal"

export default function PrivacyPolicyPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-neutral-900 to-neutral-950">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Privacy Policy</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-muted-foreground">
              Last updated: November 6, 2025
            </p>
          </Reveal>
        </div>
      </section>

      {/* Privacy Content */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-6">
          <div className="prose prose-invert max-w-none">
            <Reveal>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">1. Introduction</h2>
                <p className="text-muted-foreground mb-6">
                  At PayBridge, we are committed to protecting your privacy. This Privacy Policy explains how we collect, 
                  use, disclose, and safeguard your information when you use our Service.
                </p>
                <p className="text-muted-foreground">
                  Please read this Privacy Policy carefully. By using our Service, you agree to the collection and use of 
                  information in accordance with this policy.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={50}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">2. Information We Collect</h2>
                <p className="text-muted-foreground mb-4">We collect several different types of information for various purposes to provide and improve our Service to you.</p>
                
                <h3 className="text-xl font-semibold mt-6 mb-3">Personal Data</h3>
                <p className="text-muted-foreground mb-4">
                  While using our Service, we may ask you to provide us with certain personally identifiable information 
                  that can be used to contact or identify you ("Personal Data"). This may include:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-2 mb-4">
                  <li>Email address</li>
                  <li>First name and last name</li>
                  <li>Phone number</li>
                  <li>Business information</li>
                  <li>Payment information</li>
                </ul>

                <h3 className="text-xl font-semibold mt-6 mb-3">Usage Data</h3>
                <p className="text-muted-foreground">
                  We may also collect information on how the Service is accessed and used ("Usage Data"). This Usage Data may include 
                  information such as your computer's Internet Protocol address, browser type, browser version, the pages of our Service 
                  that you visit, the time and date of your visit, the time spent on those pages, and other diagnostic data.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={100}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">3. How We Use Your Information</h2>
                <p className="text-muted-foreground mb-4">We use the collected data for various purposes:</p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-2 mb-4">
                  <li>To provide and maintain our Service</li>
                  <li>To notify you about changes to our Service</li>
                  <li>To allow you to participate in interactive features of our Service</li>
                  <li>To provide customer support</li>
                  <li>To gather analysis or valuable information so that we can improve our Service</li>
                  <li>To monitor the usage of our Service</li>
                  <li>To detect, prevent and address technical issues</li>
                  <li>To provide you with news, special offers and general information about other goods, services and events which we offer</li>
                </ul>
              </div>
            </Reveal>

            <Reveal delayMs={150}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">4. Data Security</h2>
                <p className="text-muted-foreground mb-4">
                  The security of your data is important to us. We implement appropriate technical and organizational measures to protect 
                  the security of your personal information. However, please remember that no method of transmission over the Internet or 
                  method of electronic storage is 100% secure.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={200}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">5. Data Retention</h2>
                <p className="text-muted-foreground mb-4">
                  We will retain your Personal Data only for as long as is necessary for the purposes set out in this Privacy Policy. 
                  We will retain and use your Personal Data to the extent necessary to comply with our legal obligations, resolve disputes, 
                  and enforce our policies.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={250}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">6. Your Data Protection Rights</h2>
                <p className="text-muted-foreground mb-4">
                  Depending on your location, you may have certain rights regarding your Personal Data, including:
                </p>
                <ul className="list-disc pl-6 text-muted-foreground space-y-2 mb-4">
                  <li>The right to access, update or delete your information</li>
                  <li>The right of rectification</li>
                  <li>The right to object</li>
                  <li>The right of restriction</li>
                  <li>The right to data portability</li>
                  <li>The right to withdraw consent</li>
                </ul>
                <p className="text-muted-foreground">
                  To exercise any of these rights, please contact us using the information below.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={300}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">7. Changes to This Privacy Policy</h2>
                <p className="text-muted-foreground">
                  We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy 
                  on this page and updating the "Last updated" date at the top of this Privacy Policy.
                </p>
              </div>
            </Reveal>

            <Reveal delayMs={350}>
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-4">8. Contact Us</h2>
                <p className="text-muted-foreground mb-6">
                  If you have any questions about this Privacy Policy, please contact us:
                </p>
                <Button variant="outline">
                  Contact Us
                </Button>
              </div>
            </Reveal>
          </div>
        </div>
      </section>
    </main>
  )
}
