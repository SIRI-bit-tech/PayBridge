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
  {
    id: "paystack",
    name: "Paystack",
    logoUrl: "https://logo.clearbit.com/paystack.com",
    docsUrl: "https://paystack.com/docs"
  },
  {
    id: "flutterwave",
    name: "Flutterwave",
    logoUrl: "https://logo.clearbit.com/flutterwave.com",
    docsUrl: "https://developer.flutterwave.com/docs"
  },
  {
    id: "stripe",
    name: "Stripe",
    logoUrl: "https://logo.clearbit.com/stripe.com",
    docsUrl: "https://stripe.com/docs"
  },
  {
    id: "mono",
    name: "Mono",
    logoUrl: "https://logo.clearbit.com/mono.co",
    docsUrl: "https://mono.co/docs"
  },
  {
    id: "okra",
    name: "Okra",
    logoUrl: "https://logo.clearbit.com/okra.ng",
    docsUrl: "https://okra.ng/docs"
  },
  {
    id: "chapa",
    name: "Chapa",
    logoUrl: "https://logo.clearbit.com/chapa.co",
    docsUrl: "https://chapa.co/docs"
  },
  {
    id: "lazerpay",
    name: "Lazerpay",
    logoUrl: "https://logo.clearbit.com/lazerpay.com",
    docsUrl: "https://lazerpay.com/docs"
  },
]

// Country to Currency mapping
export const COUNTRY_CURRENCY_MAP: Record<string, string> = {
  NG: "NGN",
  GH: "GHS",
  KE: "KES",
  UG: "UGX",
  TZ: "TZS",
  ET: "ETB",
  ZA: "ZAR",
  US: "USD",
  GB: "GBP",
  CA: "CAD",
}

// Country options for signup form
export const COUNTRIES = [
  { value: "NG", label: "Nigeria" },
  { value: "GH", label: "Ghana" },
  { value: "KE", label: "Kenya" },
  { value: "UG", label: "Uganda" },
  { value: "TZ", label: "Tanzania" },
  { value: "ET", label: "Ethiopia" },
  { value: "ZA", label: "South Africa" },
  { value: "US", label: "United States" },
  { value: "GB", label: "United Kingdom" },
  { value: "CA", label: "Canada" },
]

// Currency options for signup form
export const CURRENCIES = [
  { value: "NGN", label: "NGN - Nigerian Naira" },
  { value: "GHS", label: "GHS - Ghanaian Cedi" },
  { value: "KES", label: "KES - Kenyan Shilling" },
  { value: "UGX", label: "UGX - Ugandan Shilling" },
  { value: "TZS", label: "TZS - Tanzanian Shilling" },
  { value: "ETB", label: "ETB - Ethiopian Birr" },
  { value: "ZAR", label: "ZAR - South African Rand" },
  { value: "USD", label: "USD - US Dollar" },
  { value: "GBP", label: "GBP - British Pound" },
  { value: "EUR", label: "EUR - Euro" },
  { value: "CAD", label: "CAD - Canadian Dollar" },
]

// Transaction status options
export const TRANSACTION_STATUSES = [
  { value: "completed", label: "Success" },
  { value: "pending", label: "Pending" },
  { value: "failed", label: "Failed" },
  { value: "refunded", label: "Refunded" },
  { value: "cancelled", label: "Cancelled" },
]

// Filter currency options (subset for transactions)
export const FILTER_CURRENCIES = [
  { value: "NGN", label: "NGN" },
  { value: "USD", label: "USD" },
  { value: "GBP", label: "GBP" },
  { value: "EUR", label: "EUR" },
]

// Developer type options for signup form
export const DEVELOPER_TYPES = [
  { value: "individual", label: "Individual Developer" },
  { value: "startup", label: "Startup" },
  { value: "enterprise", label: "Enterprise" },
  { value: "agency", label: "Agency" },
  { value: "other", label: "Other" },
]