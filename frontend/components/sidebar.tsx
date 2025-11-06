"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/")

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: "📊" },
    { href: "/api-keys", label: "API Keys", icon: "🔑" },
    { href: "/transactions", label: "Transactions", icon: "💳" },
    { href: "/payment-providers", label: "Providers", icon: "🏦" },
    { href: "/webhooks", label: "Webhooks", icon: "🔔" },
    { href: "/analytics", label: "Analytics", icon: "📈" },
    { href: "/billing", label: "Billing", icon: "💰" },
    { href: "/settings", label: "Settings", icon: "⚙️" },
  ]

  return (
    <aside className="w-64 border-r border-neutral-800 bg-neutral-900/50 h-screen sticky top-16 hidden md:block">
      <nav className="p-4 space-y-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
              isActive(link.href) ? "bg-primary text-white" : "text-neutral-400 hover:bg-neutral-800"
            }`}
          >
            <span>{link.icon}</span>
            <span className="text-sm">{link.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  )
}
