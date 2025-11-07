"use client"

import { useEffect, useRef, useState } from "react"

type RevealProps = {
  children: React.ReactNode
  delayMs?: number
  className?: string
}

export function Reveal({ children, delayMs = 0, className = '' }: RevealProps) {
  const ref = useRef<HTMLDivElement | null>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return
    
    let timer: ReturnType<typeof setTimeout>
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Clear any existing timer before setting a new one
            if (timer) clearTimeout(timer)
            timer = setTimeout(() => {
              setVisible(true)
              observer.unobserve(entry.target)
            }, delayMs)
          }
        })
      },
      { threshold: 0.15 }
    )
    
    observer.observe(node)
    
    // Cleanup function
    return () => {
      if (timer) clearTimeout(timer)
      observer.disconnect()
    }
  }, [delayMs])

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-in-out ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
      } ${className}`}
      style={{ transitionDelay: `${delayMs}ms` }}
    >
      {children}
    </div>
  )
}
