export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  name: string
  company_name: string
  country: string
  kyc_verified: boolean
  created_at: string
}

export interface APIKey {
  id: string
  name: string
  label?: string
  key?: string  // Only present on creation
  masked_key: string
  status: "active" | "inactive" | "revoked"
  last_used: string | null
  created_at: string
}

export interface APIKeyActivity {
  api_key_id: string
  api_key_name: string
  total_calls: number
}

export interface WebSocketMessage {
  type: 'api_key_created' | 'api_key_revoked' | 'api_key_used' | 'transaction:new' | 'transaction:update' | 'pong'
  data?: any
}

export interface Transaction {
  id: string
  reference: string
  amount: number
  currency: string
  status: "pending" | "completed" | "failed" | "cancelled" | "refunded"
  provider: string
  customer_email: string
  customer_name?: string
  description: string
  fee: number
  net_amount: number
  created_at: string
}

export interface TransactionSummary {
  total_transactions: number
  total_amount: number
  successful_count: number
  pending_count: number
  failed_count: number
  refunded_count: number
}

export interface FilterOptions {
  provider: string
  status: string
  currency: string
}

export interface PaymentProvider {
  id: string
  provider: string
  public_key: string
  is_live: boolean
  is_active: boolean
  webhook_url?: string
}

export interface Webhook {
  id: string
  url: string
  event_types: string[]
  is_active: boolean
  last_triggered: string | null
  created_at: string
}

export interface Subscription {
  id: string
  plan: "starter" | "growth" | "enterprise"
  status: "active" | "cancelled" | "expired"
  current_period_start: string
  current_period_end: string
  renewal_date: string
}

export interface Analytics {
  total_transactions: number
  total_volume: number
  success_rate: number
  average_transaction_size: number
  transactions_by_provider: Record<string, { count: number; volume: number }>
  transactions_by_status: Record<string, number>
  daily_volume: Array<{ date: string; volume: number; count: number }>
}

export interface AuthResponse {
  access: string
  refresh: string
  user: User
}
