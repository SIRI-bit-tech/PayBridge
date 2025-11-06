# PayBridge Frontend

A production-ready Next.js application for pan-African payment aggregation.

## Features

- User authentication and profile management
- API key creation and management
- Payment provider integration (Paystack, Flutterwave, Stripe, Mono, Okra, Chapa, Lazerpay)
- Transaction tracking and analytics
- Webhook management
- Billing and subscription management
- Real-time payment status updates

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

\`\`\`bash
npm install
\`\`\`

### Environment Setup

Create a `.env.local` file:

\`\`\`
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

The application will be available at `http://localhost:3000`

## Project Structure

\`\`\`
frontend/
├── app/                 # Next.js app directory
├── components/          # Reusable React components
├── lib/                 # Utility functions and API client
├── public/              # Static assets
└── README.md           # This file
\`\`\`

## Key Pages

- `/` - Homepage
- `/login` - User login
- `/signup` - User registration
- `/dashboard` - Main dashboard with statistics
- `/api-keys` - API key management
- `/transactions` - Transaction history
- `/payment-providers` - Payment provider configuration
- `/webhooks` - Webhook management
- `/billing` - Subscription and billing
- `/settings` - Account settings

## API Integration

The frontend communicates with the Django backend via REST API. All API calls are handled through the `apiCall` function in `lib/api.ts`.

Authentication is done via JWT tokens stored in localStorage.

## Deployment

### Deploy to Vercel

\`\`\`bash
vercel
\`\`\`

### Environment Variables

Set the following environment variable in your deployment platform:

- `NEXT_PUBLIC_API_BASE_URL` - Your Django API base URL

## Support

For issues and questions, please refer to the API documentation or contact support.
