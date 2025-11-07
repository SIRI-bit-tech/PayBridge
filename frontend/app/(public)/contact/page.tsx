"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Reveal } from "@/components/Reveal"
import { Mail, Phone, MapPin, Send, CheckCircle } from "lucide-react"

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setIsSubmitting(false)
    setIsSubmitted(true)
    
    // Reset form after submission
    setTimeout(() => {
      setFormData({
        name: "",
        email: "",
        subject: "",
        message: ""
      })
      setIsSubmitted(false)
    }, 5000)
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      {/* Hero Section */}
      <section className="relative py-20 bg-gradient-to-b from-neutral-900 to-neutral-950">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Reveal>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Contact Us</h1>
          </Reveal>
          <Reveal delayMs={100}>
            <p className="text-xl text-neutral-300">
              We'd love to hear from you. Get in touch with our team.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12">
            {/* Contact Form */}
            <Reveal>
              <div className="bg-neutral-900/60 p-8 rounded-xl border border-neutral-800">
                <h2 className="text-2xl font-bold mb-6">Send us a message</h2>
                
                {isSubmitted ? (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">Message Sent Successfully!</h3>
                    <p className="text-neutral-300">We'll get back to you within 24 hours.</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-neutral-300 mb-2">
                          Full Name *
                        </label>
                        <Input
                          id="name"
                          name="name"
                          type="text"
                          required
                          value={formData.name}
                          onChange={handleChange}
                          className="bg-neutral-800 border-neutral-700 text-white"
                        />
                      </div>
                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-neutral-300 mb-2">
                          Email Address *
                        </label>
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          required
                          value={formData.email}
                          onChange={handleChange}
                          className="bg-neutral-800 border-neutral-700 text-white"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label htmlFor="subject" className="block text-sm font-medium text-neutral-300 mb-2">
                        Subject *
                      </label>
                      <Input
                        id="subject"
                        name="subject"
                        type="text"
                        required
                        value={formData.subject}
                        onChange={handleChange}
                        className="bg-neutral-800 border-neutral-700 text-white"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="message" className="block text-sm font-medium text-neutral-300 mb-2">
                        Your Message *
                      </label>
                      <Textarea
                        id="message"
                        name="message"
                        rows={5}
                        required
                        value={formData.message}
                        onChange={handleChange}
                        className="bg-neutral-800 border-neutral-700 text-white"
                      />
                    </div>
                    
                    <Button 
                      type="submit" 
                      className="w-full"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? (
                        'Sending...'
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Send Message
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </div>
            </Reveal>

            {/* Contact Information */}
            <Reveal delayMs={100}>
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-bold mb-6">Get in touch</h2>
                  <p className="text-neutral-300 mb-8">
                    Have questions about our platform or need assistance? Our team is here to help. 
                    Reach out to us using the information below or fill out the contact form.
                  </p>
                </div>

                <div className="space-y-6">
                  <div className="flex items-start">
                    <div className="bg-blue-600/20 p-3 rounded-lg mr-4">
                      <Mail className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-medium">Email Us</h3>
                      <a href="mailto:support@paybridge.com" className="text-blue-400 hover:underline">
                        support@paybridge.com
                      </a>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="bg-green-600/20 p-3 rounded-lg mr-4">
                      <Phone className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <h3 className="font-medium">Call Us</h3>
                      <a href="tel:+1234567890" className="text-blue-400 hover:underline">
                        +1 (234) 567-890
                      </a>
                      <p className="text-sm text-neutral-400 mt-1">Mon-Fri from 9am to 5pm</p>
                    </div>
                  </div>

                  <div className="flex items-start">
                    <div className="bg-purple-600/20 p-3 rounded-lg mr-4">
                      <MapPin className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="font-medium">Visit Us</h3>
                      <p className="text-neutral-300">
                        123 Payment Street<br />
                        San Francisco, CA 94103<br />
                        United States
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-6 border-t border-neutral-800">
                  <h3 className="font-medium mb-4">Follow Us</h3>
                  <div className="flex space-x-4">
                    {[
                      { name: 'Twitter', icon: '🐦' },
                      { name: 'LinkedIn', icon: '💼' },
                      { name: 'GitHub', icon: '💻' },
                      { name: 'Facebook', icon: '👍' },
                      { name: 'Instagram', icon: '📷' }
                    ].map((social, index) => (
                      <a 
                        key={index} 
                        href="#" 
                        className="w-10 h-10 flex items-center justify-center rounded-full bg-neutral-800 hover:bg-neutral-700 transition-colors"
                        aria-label={social.name}
                      >
                        <span className="text-lg">{social.icon}</span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="py-16 bg-neutral-900/30">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <Reveal>
              <h2 className="text-2xl font-bold mb-3">Our Office</h2>
              <p className="text-neutral-300">Visit our headquarters in the heart of San Francisco</p>
            </Reveal>
          </div>
          
          <Reveal delayMs={100}>
            <div className="bg-neutral-800 rounded-xl overflow-hidden h-96 relative">
              {/* Placeholder for map - in a real app, you'd use a map component here */}
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-900/50 to-purple-900/50">
                <div className="text-center p-6 bg-neutral-900/80 rounded-lg">
                  <MapPin className="w-8 h-8 mx-auto mb-2 text-blue-400" />
                  <p className="text-lg font-medium">PayBridge Headquarters</p>
                  <p className="text-neutral-300">123 Payment Street, San Francisco, CA</p>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>
    </main>
  )
}

