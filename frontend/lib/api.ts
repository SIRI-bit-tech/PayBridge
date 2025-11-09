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
  let token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null

  const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ...(options.headers || {})
  } as Record<string, string>

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  try {
    let response = await retryWithBackoff(() =>
      fetch(url, {
        ...options,
        headers,
        credentials: options.credentials || 'include',
      }),
    )

    // If 401 and we have a refresh token, try to refresh
    if (response.status === 401 && typeof window !== "undefined") {
      const newToken = await refreshToken();
      if (newToken) {
        headers["Authorization"] = `Bearer ${newToken}`;
        response = await fetch(url, {
          ...options,
          headers,
          credentials: options.credentials || 'include',
        });
      } else {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (typeof window !== "undefined" && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        return { error: "Session expired", status: 401 };
      }
    }

    const data = await response.json()

    if (response.ok) {
      return { data, status: response.status }
    } else {
      return { error: data.detail || data.error || "An error occurred", status: response.status }
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Network error"
    console.log(" API call failed:", errorMessage)
    return {
      error: errorMessage,
      status: 0,
    }
  }
}

export interface LoginCredentials {
  email?: string;
  phone_number?: string;
  password: string;
  remember_me?: boolean;
}

export async function login(credentials: LoginCredentials) {
  const response = await apiCall<{ access: string; refresh: string; user: any }>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
    credentials: 'include',
  });
  
  // Store tokens in localStorage
  if (response.data) {
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
  }
  
  return response;
}

export async function refreshToken(): Promise<string | null> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return null;
  
  try {
    const response = await fetch(`${API_BASE_URL_ENV}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access);
      return data.access;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
  
  return null;
}

export async function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  return { data: { message: 'Logged out successfully' }, status: 200 };
}

export async function requestPasswordReset(emailOrPhone: string) {
  return apiCall('/auth/password/reset/', {
    method: 'POST',
    body: JSON.stringify({ email_or_phone: emailOrPhone }),
  });
}

export async function resetPassword(uid: string, token: string, newPassword: string) {
  return apiCall('/auth/password/reset/confirm/', {
    method: 'POST',
    body: JSON.stringify({
      uid,
      token,
      new_password: newPassword,
    }),
  });
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
  // Try GraphQL first
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
  
  const graphqlResponse = await graphQLQuery<any>(query)
  
  // If GraphQL works, return it
  if (graphqlResponse.data?.analytics) {
    return {
      data: graphqlResponse.data.analytics,
      status: graphqlResponse.status
    }
  }
  
  // Fallback to REST API
  const restResponse = await apiCall<any>("/analytics/dashboard/")
  
  if (restResponse.data) {
    return {
      data: restResponse.data,
      status: restResponse.status
    }
  }
  
  return graphqlResponse // Return original error
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
