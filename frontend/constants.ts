export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.paybridge.local"
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || "ws://localhost:8000"
export const APP_NAME = "PayBridge"

export const COLORS = {
  PRIMARY: "#101820", // Obsidian Black
  ACCENT: "#007BFF", // Electric Blue
  HOVER: "#339CFF", // Hover/Focus Blue
  TEXT_GRAY: "#B5B5C3", // Muted Text Gray
  SUCCESS: "#10B981", // Green
  ERROR: "#EF4444", // Red
  WARNING: "#F59E0B", // Amber
  BACKGROUND: "#0F1419", // Dark Background
  CARD_BG: "#1A1F2E", // Card Background
}

export const BILLING_PLANS = {
  STARTER: {
    name: "Starter",
    price: 29,
    api_calls_limit: 10000,
    features: ["10K API calls/month", "Basic analytics", "1 webhook", "Email support"],
  },
  GROWTH: {
    name: "Growth",
    price: 99,
    api_calls_limit: 100000,
    features: ["100K API calls/month", "Advanced analytics", "5 webhooks", "Priority support"],
  },
  ENTERPRISE: {
    name: "Enterprise",
    price: null,
    api_calls_limit: null,
    features: ["Unlimited API calls", "Custom analytics", "Unlimited webhooks", "Dedicated support"],
  },
}

export const PAYMENT_PROVIDERS = [
  { id: "paystack", name: "Paystack", icon: "🏦" },
  { id: "flutterwave", name: "Flutterwave", icon: "🌊" },
  { id: "stripe", name: "Stripe", icon: "💳" },
  { id: "mono", name: "Mono", icon: "🔗" },
  { id: "okra", name: "Okra", icon: "🌾" },
  { id: "chapa", name: "Chapa", icon: "🇪🇹" },
  { id: "lazerpay", name: "Lazerpay", icon: "⚡" },
]
