import type { Analytics } from "@/types"

const API_BASE_URL_ENV = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1"
const MAX_RETRIES = 3
const INITIAL_RETRY_DELAY = 1000 // 1 second

export interface ApiResponse<T> {
  data?: T
  error?: string
  errors?: Record<string, string[]>
  status: number
}

async function retryWithBackoff<T>(fn: () => Promise<T>, maxRetries: number = MAX_RETRIES): Promise<T> {
  let lastError: Error | undefined

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      // Only retry on network errors, not on HTTP errors
      if (!(error instanceof TypeError && error.message.includes("Failed to fetch"))) {
        throw error
      }

      if (attempt < maxRetries - 1) {
        const delayMs = INITIAL_RETRY_DELAY * Math.pow(2, attempt)
        await new Promise((resolve) => setTimeout(resolve, delayMs))
      }
    }
  }

  throw lastError || new Error("Request failed after retries")
}

function generateIdempotentKey(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL_ENV}${endpoint}`
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ...(options.headers || {})
  } as Record<string, string>

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  try {
    const response = await retryWithBackoff(() =>
      fetch(url, {
        ...options,
        headers,
      }),
    )

    const data = await response.json()

    if (response.ok) {
      return { data, status: response.status }
    } else {
      return { error: data.detail || "An error occurred", status: response.status }
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Network error"
    console.log("[v0] API call failed:", errorMessage)
    return {
      error: errorMessage,
      status: 0,
    }
  }
}

export async function login(email: string, password: string) {
  return apiCall("/auth/token/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  })
}

export async function register(data: {
  first_name: string
  last_name: string
  email: string
  phone_number: string
  country: string
  password: string
  confirm_password: string
  company_name?: string
  developer_type?: string
  preferred_currency?: string
  terms_accepted: boolean
}) {
  const payload = {
    ...data,
    terms_accepted: Boolean(data.terms_accepted)
  }
  
  return apiCall("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    }
  })
}

export async function getProfile() {
  return apiCall("/profile/me/")
}

export async function updateProfile(data: any) {
  return apiCall("/profile/me/", {
    method: "PUT",
    body: JSON.stringify(data),
  })
}

export async function getApiKeys() {
  return apiCall("/api-keys/")
}

export async function createApiKey(name: string) {
  return apiCall("/api-keys/", {
    method: "POST",
    body: JSON.stringify({ name }),
  })
}

export async function revokeApiKey(id: string) {
  return apiCall(`/api-keys/${id}/revoke/`, {
    method: "POST",
  })
}

export async function getPaymentProviders() {
  return apiCall("/payment-providers/")
}

export async function createPaymentProvider(data: any) {
  return apiCall("/payment-providers/", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function getTransactions() {
  return apiCall("/transactions/")
}

export async function initiatePayment(data: any) {
  const paymentData = {
    ...data,
    idempotency_key: generateIdempotentKey(),
    use_tokenization: true, // Force Stripe tokenization for card payments
    save_card: false, // Never save card details
  }

  return apiCall("/transactions/initiate_payment/", {
    method: "POST",
    body: JSON.stringify(paymentData),
    headers: {
      "Idempotency-Key": paymentData.idempotency_key,
    },
  })
}

export async function verifyPayment(transactionId: string) {
  return apiCall(`/transactions/${transactionId}/verify_payment/`)
}

export async function getWebhooks() {
  return apiCall("/webhooks/")
}

export async function createWebhook(data: any) {
  return apiCall("/webhooks/", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function deleteWebhook(id: string) {
  return apiCall(`/webhooks/${id}/`, {
    method: "DELETE",
  })
}

export async function getSubscription() {
  return apiCall("/subscriptions/current/")
}

export async function getAuditLogs() {
  return apiCall("/audit-logs/")
}

export async function graphQLQuery<T>(query: string, variables?: Record<string, any>): Promise<ApiResponse<T>> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  try {
    const response = await retryWithBackoff(() =>
      fetch(`${API_BASE_URL_ENV}/graphql/`, {
        method: "POST",
        headers,
        body: JSON.stringify({ query, variables }),
      }),
    )

    const data = await response.json()

    if (response.ok && !data.errors) {
      return { data: data.data as T, status: response.status }
    } else {
      return {
        error: data.errors?.[0]?.message || "GraphQL error",
        status: response.status,
      }
    }
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : "Network error",
      status: 0,
    }
  }
}

export async function getAnalytics(): Promise<ApiResponse<Analytics>> {
  const query = `
    query {
      analytics {
        totalTransactions
        totalVolume
        successRate
        averageTransactionSize
        transactionsByProvider
        transactionsByStatus
        dailyVolume
      }
    }
  `
  return graphQLQuery<Analytics>(query)
}

export async function getTransactionsAdvanced(filters?: {
  provider?: string
  status?: string
  currency?: string
}) {
  const query = `
    query GetTransactions($provider: String, $status: String, $currency: String) {
      transactions(provider: $provider, status: $status, currency: $currency) {
        edges {
          node {
            id
            reference
            amount
            currency
            status
            provider
            customerEmail
            description
            fee
            netAmount
            createdAt
          }
        }
      }
    }
  `
  return graphQLQuery<any>(query, filters)
}

export async function createStripeConnectAccount(data: { country: string; business_type: string }) {
  return apiCall("/stripe/connect/account/", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function getStripeConnectStatus() {
  return apiCall("/stripe/connect/status/")
}

export async function createStripeConnectPayment(data: any) {
  const paymentData = {
    ...data,
    idempotency_key: generateIdempotentKey(),
    use_tokenization: true,
    save_card: false,
  }

  return apiCall("/payments/stripe-connect/", {
    method: "POST",
    body: JSON.stringify(paymentData),
    headers: {
      "Idempotency-Key": paymentData.idempotency_key,
    },
  })
}
