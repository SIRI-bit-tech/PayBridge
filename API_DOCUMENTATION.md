# PayBridge API Documentation

## Base URL

\`\`\`
https://api.yourdomain.com/api/v1
\`\`\`

## Authentication

All endpoints require JWT authentication (except login/signup).

**Include in headers:**
\`\`\`
Authorization: Bearer <access_token>
\`\`\`

## Authentication Endpoints

### Obtain Tokens

**POST** `/auth/token/`

Request body:
\`\`\`json
{
  "email": "user@example.com",
  "password": "password123"
}
\`\`\`

Response (200):
\`\`\`json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

### Refresh Token

**POST** `/auth/token/refresh/`

Request body:
\`\`\`json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
\`\`\`

## Profile Endpoints

### Get Profile

**GET** `/profile/me/`

Response (200):
\`\`\`json
{
  "email": "user@example.com",
  "company_name": "Acme Inc",
  "country": "NG",
  "phone_number": "+234123456789",
  "business_type": "E-commerce",
  "kyc_verified": false
}
\`\`\`

### Update Profile

**PUT** `/profile/me/`

Request body:
\`\`\`json
{
  "company_name": "New Company Name",
  "country": "GH",
  "phone_number": "+233123456789",
  "business_type": "SaaS"
}
\`\`\`

## API Keys Endpoints

### List API Keys

**GET** `/api-keys/`

Response (200):
\`\`\`json
{
  "count": 2,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Production Key",
      "key": "pk_live_abcd1234",
      "status": "active",
      "last_used": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
\`\`\`

### Create API Key

**POST** `/api-keys/`

Request body:
\`\`\`json
{
  "name": "My API Key"
}
\`\`\`

Response (201):
\`\`\`json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My API Key",
  "key": "pk_live_abcd1234",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
\`\`\`

### Revoke API Key

**POST** `/api-keys/{id}/revoke/`

Response (200):
\`\`\`json
{
  "status": "API key revoked"
}
\`\`\`

## Payment Provider Endpoints

### List Providers

**GET** `/payment-providers/`

Response (200):
\`\`\`json
{
  "count": 1,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "provider": "paystack",
      "is_live": false,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
\`\`\`

### Configure Provider

**POST** `/payment-providers/`

Request body:
\`\`\`json
{
  "provider": "paystack",
  "public_key": "pk_test_xxxxx",
  "secret_key": "sk_test_xxxxx"
}
\`\`\`

## Transaction Endpoints

### List Transactions

**GET** `/transactions/?status=completed&limit=10`

Response (200):
\`\`\`json
{
  "count": 150,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "reference": "paystack_1234567890",
      "amount": 50000,
      "currency": "NGN",
      "status": "completed",
      "provider": "paystack",
      "customer_email": "customer@example.com",
      "description": "Product purchase",
      "fee": 1250,
      "net_amount": 48750,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
\`\`\`

### Initiate Payment

**POST** `/transactions/initiate_payment/`

Request body:
\`\`\`json
{
  "api_key_id": "550e8400-e29b-41d4-a716-446655440000",
  "provider": "paystack",
  "amount": 50000,
  "currency": "NGN",
  "customer_email": "customer@example.com",
  "description": "Product purchase"
}
\`\`\`

Response (201):
\`\`\`json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "reference": "paystack_1234567890",
  "amount": 50000,
  "currency": "NGN",
  "status": "pending",
  "provider": "paystack",
  "customer_email": "customer@example.com",
  "fee": 1250,
  "net_amount": 48750,
  "created_at": "2024-01-15T10:30:00Z"
}
\`\`\`

### Verify Payment

**GET** `/transactions/{id}/verify_payment/`

Response (200):
\`\`\`json
{
  "status": "success",
  "reference": "paystack_1234567890",
  "amount": 50000,
  "paid_at": "2024-01-15T10:35:00Z"
}
\`\`\`

## Webhook Endpoints

### List Webhooks

**GET** `/webhooks/`

Response (200):
\`\`\`json
{
  "count": 1,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://your-server.com/webhooks/paybridge",
      "event_types": ["payment.completed", "payment.failed"],
      "is_active": true,
      "last_triggered": "2024-01-15T10:35:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
\`\`\`

### Create Webhook

**POST** `/webhooks/`

Request body:
\`\`\`json
{
  "url": "https://your-server.com/webhooks/paybridge",
  "event_types": ["payment.completed", "payment.failed"]
}
\`\`\`

### Delete Webhook

**DELETE** `/webhooks/{id}/`

Response (204): No content

## Webhook Events

### Payment Completed

\`\`\`json
{
  "event": "payment.completed",
  "transaction": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "reference": "paystack_1234567890",
    "amount": 50000,
    "currency": "NGN",
    "status": "completed",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
\`\`\`

### Payment Failed

\`\`\`json
{
  "event": "payment.failed",
  "transaction": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "reference": "paystack_1234567890",
    "amount": 50000,
    "currency": "NGN",
    "status": "failed",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
\`\`\`

## Subscription Endpoints

### Get Current Subscription

**GET** `/subscriptions/current/`

Response (200):
\`\`\`json
{
  "plan": "growth",
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-02-01T00:00:00Z",
  "renewal_date": "2024-02-01T00:00:00Z"
}
\`\`\`

## Error Responses

### 400 Bad Request

\`\`\`json
{
  "error": "Invalid request"
}
\`\`\`

### 401 Unauthorized

\`\`\`json
{
  "error": "Invalid or expired token"
}
\`\`\`

### 404 Not Found

\`\`\`json
{
  "error": "Resource not found"
}
\`\`\`

### 500 Internal Server Error

\`\`\`json
{
  "error": "Internal server error"
}
\`\`\`

## Rate Limiting

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## SDK Integration Example

\`\`\`bash
# Using curl
curl -X GET https://api.yourdomain.com/api/v1/profile/me/ \
  -H "Authorization: Bearer <access_token>"

# Using Python
import requests

headers = {
  "Authorization": "Bearer <access_token>"
}
response = requests.get(
  "https://api.yourdomain.com/api/v1/profile/me/",
  headers=headers
)
\`\`\`

---

For more details, visit https://yourdomain.com/api/docs/
