# PayBridge Backend API

A production-ready Django REST API for pan-African payment aggregation.

## Features

- User authentication with JWT
- API key management
- Payment provider integration
- Transaction processing and tracking
- Webhook support for all payment providers
- Real-time payment status updates
- Comprehensive audit logging
- Row-level security (RLS)

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis (for Celery tasks and caching)

### Installation

1. Clone the repository and navigate to the backend directory

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Create a `.env` file based on `.env.example`:
\`\`\`bash
cp .env.example .env
\`\`\`

5. Configure your environment variables (database, email, payment providers)

6. Run migrations:
\`\`\`bash
python manage.py migrate
\`\`\`

7. Create a superuser:
\`\`\`bash
python manage.py createsuperuser
\`\`\`

8. Start the development server:
\`\`\`bash
python manage.py runserver
\`\`\`

The API will be available at `http://localhost:8000`

## Project Structure

\`\`\`
backend/
├── paybridge/          # Django project settings
├── api/                # Main API app
│   ├── models.py       # Database models
│   ├── views.py        # API viewsets
│   ├── serializers.py  # DRF serializers
│   ├── urls.py         # API routes
│   ├── admin.py        # Django admin configuration
│   ├── payment_handlers.py  # Payment provider handlers
│   └── webhook_views.py     # Webhook endpoints
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
\`\`\`

## API Endpoints

### Authentication
- `POST /api/v1/auth/token/` - Obtain JWT tokens
- `POST /api/v1/auth/token/refresh/` - Refresh access token

### Profile
- `GET /api/v1/profile/me/` - Get user profile
- `PUT /api/v1/profile/me/` - Update user profile

### API Keys
- `GET /api/v1/api-keys/` - List API keys
- `POST /api/v1/api-keys/` - Create new API key
- `POST /api/v1/api-keys/{id}/revoke/` - Revoke API key

### Payment Providers
- `GET /api/v1/payment-providers/` - List configured providers
- `POST /api/v1/payment-providers/` - Configure payment provider

### Transactions
- `GET /api/v1/transactions/` - List transactions
- `POST /api/v1/transactions/initiate_payment/` - Initiate payment
- `GET /api/v1/transactions/{id}/verify_payment/` - Verify payment

### Webhooks
- `GET /api/v1/webhooks/` - List webhooks
- `POST /api/v1/webhooks/` - Create webhook
- `DELETE /api/v1/webhooks/{id}/` - Delete webhook

### Webhook Events
- `POST /api/v1/webhooks/paystack/` - Paystack webhook
- `POST /api/v1/webhooks/flutterwave/` - Flutterwave webhook
- `POST /api/v1/webhooks/stripe/` - Stripe webhook
- `POST /api/v1/webhooks/chapa/` - Chapa webhook

## Database Models

### UserProfile
- Stores user company information and KYC status

### APIKey
- User API keys for authentication
- Status tracking (active, inactive, revoked)

### PaymentProvider
- Configured payment provider credentials
- Live/test mode toggle

### Transaction
- Complete transaction records
- Status tracking and provider responses

### Webhook
- User webhook endpoints
- Event type subscriptions
- Retry tracking

### Subscription
- User subscription plans
- Billing period tracking

### AuditLog
- All user actions logged
- IP address and user agent tracking

## Payment Provider Integration

### Paystack
- Requires: Public Key, Secret Key
- Webhook Signature: X-Paystack-Signature header

### Flutterwave
- Requires: Public Key, Secret Key
- Webhook Signature: Verif-Hash header

### Stripe
- Requires: API Key, Webhook Secret
- Uses standard Stripe event format

### Chapa
- Requires: API Key
- Webhook Signature: X-Chapa-Signature header

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. Obtain tokens via `/api/v1/auth/token/`
2. Include in headers: `Authorization: Bearer <access_token>`
3. Refresh tokens via `/api/v1/auth/token/refresh/`

## Webhook Signature Verification

All webhooks are verified using HMAC-SHA256 (or provider-specific method).

Example verification:
\`\`\`python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    computed = hmac.new(secret.encode(), payload, hashlib.sha512).hexdigest()
    return computed == signature
\`\`\`

## Deployment

### Docker

\`\`\`dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "paybridge.wsgi:application", "--bind", "0.0.0.0:8000"]
\`\`\`

### Render.com

1. Connect your GitHub repository
2. Set environment variables
3. Deploy with `gunicorn paybridge.wsgi:application`

### AWS EC2

1. Install Python, PostgreSQL, Redis
2. Clone repository and install dependencies
3. Use systemd service for auto-restart
4. Configure Nginx as reverse proxy
5. Use Certbot for SSL certificates

## Environment Variables

See `.env.example` for complete list. Key variables:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (False in production)
- `ALLOWED_HOSTS` - Allowed domain names
- `DB_*` - Database configuration
- `PAYSTACK_*` - Paystack credentials
- `FLUTTERWAVE_*` - Flutterwave credentials
- `STRIPE_*` - Stripe credentials
- etc.

## Monitoring & Logging

- All API requests are logged
- Audit logs track user actions
- Integration with monitoring services (e.g., Sentry)

## Support

For issues and API documentation, please refer to the OpenAPI schema at `/api/schema/`
