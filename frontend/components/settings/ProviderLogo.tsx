"use client"

import { useState } from "react"
import Image from "next/image"

export function ProviderLogo({ provider, size = "md" }: { provider: string; size?: "sm" | "md" | "lg" }) {
  const [imageError, setImageError] = useState(false)
  
  const sizeMap = {
    sm: 16,
    md: 24,
    lg: 32
  }
  
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8"
  }
  
  // SVG fallback logos
  const svgLogos = {
    paystack: (
      <svg viewBox="0 0 200 200" className={sizeClasses[size]} fill="none">
        <rect width="200" height="200" rx="20" fill="#00C3F7"/>
        <path d="M60 70h80v15H60V70zm0 30h80v15H60v-15zm0 30h50v15H60v-15z" fill="white"/>
      </svg>
    ),
    flutterwave: (
      <svg viewBox="0 0 200 200" className={sizeClasses[size]} fill="none">
        <rect width="200" height="200" rx="20" fill="#F5A623"/>
        <path d="M70 60l60 40-60 40V60z" fill="white"/>
      </svg>
    ),
    stripe: (
      <svg viewBox="0 0 200 200" className={sizeClasses[size]} fill="none">
        <rect width="200" height="200" rx="20" fill="#635BFF"/>
        <path d="M100 70c-16.5 0-30 13.5-30 30s13.5 30 30 30 30-13.5 30-30-13.5-30-30-30z" fill="white"/>
      </svg>
    )
  }
  
  const logoUrls = {
    paystack: "https://upload.wikimedia.org/wikipedia/commons/0/0b/Paystack_Logo.png",
    flutterwave: "https://upload.wikimedia.org/wikipedia/commons/9/9e/Flutterwave_Logo.png",
    stripe: "https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg"
  }
  
  const logoUrl = logoUrls[provider as keyof typeof logoUrls]
  const svgLogo = svgLogos[provider as keyof typeof svgLogos]
  
  // Use SVG fallback if image fails to load
  if (imageError || !logoUrl) {
    return svgLogo || (
      <div className={`${sizeClasses[size]} rounded bg-gray-500 flex items-center justify-center text-white text-xs font-bold`}>
        {provider[0].toUpperCase()}
      </div>
    )
  }
  
  return (
    <div className={`${sizeClasses[size]} relative flex items-center justify-center`}>
      <Image
        src={logoUrl}
        alt={`${provider} logo`}
        width={sizeMap[size]}
        height={sizeMap[size]}
        className="object-contain"
        onError={() => setImageError(true)}
      />
    </div>
  )
}
