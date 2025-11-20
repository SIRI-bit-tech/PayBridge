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

// Webhook Types
export interface WebhookSubscription {
  id: string
  url: string
  masked_secret: string
  selected_events: string[]
  active: boolean
  health_status: 'healthy' | 'degraded' | 'failing' | 'disabled'
  last_delivery_at: string | null
  failure_count: number
  success_count: number
  created_at: string
  updated_at: string
}

export interface WebhookEvent {
  id: string
  provider: 'paystack' | 'flutterwave' | 'stripe' | 'mono'
  provider_event_id: string
  canonical_event_type: string
  raw_payload: any
  signature_valid: boolean
  received_at: string
  processed_at: string | null
  processing_status: 'pending' | 'processing' | 'succeeded' | 'failed'
  processing_error: string
  created_at: string
}

export interface WebhookDeliveryLog {
  id: string
  webhook_subscription: string
  webhook_url: string
  webhook_event: string | null
  event_id: string
  event_type: string
  attempt_number: number
  status: 'pending' | 'success' | 'failed' | 'dead_letter'
  http_status_code: number | null
  response_body: string
  latency_ms: number | null
  error_message: string
  next_retry_at: string | null
  created_at: string
}

export interface WebhookDeliveryMetrics {
  id: string
  webhook_subscription: string
  period_start: string
  period_end: string
  total_deliveries: number
  successful_deliveries: number
  failed_deliveries: number
  retry_count: number
  dead_letter_count: number
  avg_latency_ms: number
  p95_latency_ms: number
  p99_latency_ms: number
  success_rate: number
}

export interface WebhookDashboard {
  total_subscriptions: number
  active_subscriptions: number
  total_deliveries_24h: number
  successful_deliveries_24h: number
  failed_deliveries_24h: number
  dead_letter_deliveries_24h: number
  success_rate: number
  avg_latency_ms: number
  failing_endpoints: Array<{
    url: string
    last_delivery_status: string
    failure_count: number
  }>
}

export interface AvailableWebhookEvent {
  type: string
  description: string
}

// Legacy webhook type (deprecated)
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

// Settings Types
export interface BusinessProfile {
  id: string
  company_name: string
  business_phone: string
  business_type: string
  country: string
  business_email?: string
  business_address?: string
  tax_id?: string
  website?: string
  created_at: string
  updated_at: string
}

export interface PaymentProviderConfig {
  id: string
  provider: 'paystack' | 'flutterwave' | 'stripe'
  mode: 'test' | 'live'
  is_active: boolean
  is_primary: boolean
  public_key_masked: string
  secret_key_masked: string
  credentials_validated: boolean
  last_validated_at: string | null
  validation_error: string
  webhook_url?: string
  created_at: string
  updated_at: string
}

export interface SettingsWebSocketMessage {
  type: 'settings:profile_updated' | 'settings:provider_updated' | 'settings:provider_added' | 'settings:provider_deleted' | 'settings:provider_mode_changed'
  data: any
}
