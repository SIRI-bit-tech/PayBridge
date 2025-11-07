"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const links = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/api-keys", label: "API Keys", icon: "🔑" },
  { href: "/transactions", label: "Transactions", icon: "💳" },
  { href: "/billing", label: "Billing", icon: "💰" },
  { href: "/webhooks", label: "Webhooks", icon: "🪝" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col h-screen">
      <div className="p-6 border-b border-sidebar-border">
        <h1 className="text-2xl font-bold text-primary">PayBridge</h1>
      </div>
      <nav className="flex-1 p-6 space-y-2 overflow-y-auto">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              pathname.startsWith(link.href.split("/")[1])
                ? "bg-sidebar-primary text-sidebar-primary-foreground"
                : "text-sidebar-foreground/70 hover:bg-sidebar-accent",
            )}
          >
            <span className="text-xl">{link.icon}</span>
            <span className="font-medium">{link.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  )
}
