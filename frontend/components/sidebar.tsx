"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  KeyRound,
  CreditCard,
  Building2,
  Webhook,
  BarChart3,
  Receipt,
  Settings,
  Zap,
} from "lucide-react"

export function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/")

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/unified-payment", label: "Unified Payment", icon: Zap },
    { href: "/api-keys", label: "API Keys", icon: KeyRound },
    { href: "/transactions", label: "Transactions", icon: CreditCard },
    { href: "/payment-providers", label: "Providers", icon: Building2 },
    { href: "/webhooks", label: "Webhooks", icon: Webhook },
    { href: "/analytics", label: "Analytics", icon: BarChart3 },
    { href: "/billing", label: "Billing", icon: Receipt },
    { href: "/settings", label: "Settings", icon: Settings },
  ]

  return (
    <aside className="w-64 border-r border-border bg-card/50 h-screen sticky top-16 hidden md:block">
      <nav className="p-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                isActive(link.href) ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="text-sm">{link.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
