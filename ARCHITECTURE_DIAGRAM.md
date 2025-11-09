# PayBridge Live Dashboard - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                    Next.js Frontend (Port 3000)                 │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │  Dashboard   │  │  Components  │  │   API Client │        │   │
│  │  │    Page      │  │  - Recent    │  │  - GraphQL   │        │   │
│  │  │              │  │    Txns      │  │  - WebSocket │        │   │
│  │  │  - Analytics │  │  - Activity  │  │  - REST      │        │   │
│  │  │  - Charts    │  │  - Settlement│  │              │        │   │
│  │  │  - Metrics   │  │  - Health    │  │              │        │   │
│  │  │              │  │  - User      │  │              │        │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │   │
│  └─────────┼──────────────────┼──────────────────┼───────────────┘   │
└────────────┼──────────────────┼──────────────────┼────────────────────┘
             │                  │                  │
             │ HTTP/GraphQL     │ WebSocket        │ HTTP/REST
             │                  │                  │
┌────────────▼──────────────────▼──────────────────▼────────────────────┐
│                    Django Backend (Port 8000)                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      ASGI Application                            │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  │
│  │  │   GraphQL    │  │  WebSocket   │  │   REST API   │         │  │
│  │  │   Endpoint   │  │  Consumers   │  │   ViewSets   │         │  │
│  │  │              │  │              │  │              │         │  │
│  │  │  /graphql/   │  │  Dashboard   │  │  Settlement  │         │  │
│  │  │              │  │  Transaction │  │  Analytics   │         │  │
│  │  │  - Schema    │  │              │  │  Profile     │         │  │
│  │  │  - Resolvers │  │  - Events    │  │  Txns        │         │  │
│  │  │  - Types     │  │  - Updates   │  │  Webhooks    │         │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │  │
│  └─────────┼──────────────────┼──────────────────┼────────────────┘  │
│            │                  │                  │                     │
│            │                  │                  │                     │
│  ┌─────────▼──────────────────▼──────────────────▼────────────────┐  │
│  │                      Business Logic Layer                        │  │
│  │                                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  │
│  │  │   Models     │  │  Serializers │  │   Services   │         │  │
│  │  │              │  │              │  │              │         │  │
│  │  │  Transaction │  │  GraphQL     │  │  Settlement  │         │  │
│  │  │  Settlement  │  │  REST        │  │  Analytics   │         │  │
│  │  │  APILog      │  │              │  │  Webhook     │         │  │
│  │  │  Webhook     │  │              │  │              │         │  │
│  │  │  User        │  │              │  │              │         │  │
│  │  └──────┬───────┘  └──────────────┘  └──────────────┘         │  │
│  └─────────┼──────────────────────────────────────────────────────┘  │
│            │                                                           │
└────────────┼───────────────────────────────────────────────────────────┘
             │
             │ ORM Queries
             │
┌────────────▼───────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                                │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │ Transactions │  │  Settlements │  │   API Logs   │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   Webhooks   │  │    Users     │  │   Providers  │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                      Redis (Channel Layer)                                │
│                                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │  WebSocket   │  │    Cache     │  │   Sessions   │                 │
│  │   Channels   │  │              │  │              │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. GraphQL Query Flow

```
User Action (Dashboard Load)
        │
        ▼
┌───────────────────┐
│  Frontend sends   │
│  GraphQL query    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  GraphQL Endpoint │
│  /api/v1/graphql/ │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Schema Resolver  │
│  - analytics()    │
│  - transactions() │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Database Query   │
│  - Aggregations   │
│  - Joins          │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  JSON Response    │
│  to Frontend      │
└───────────────────┘
```

### 2. WebSocket Real-time Flow

```
User Connects to Dashboard
        │
        ▼
┌───────────────────┐
│  WebSocket Client │
│  connects to      │
│  /ws/dashboard/   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  DashboardConsumer│
│  - Authenticate   │
│  - Join room      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Subscribe to     │
│  - analytics      │
│  - transactions   │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Backend Event    │
│  (New Transaction)│
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Channel Layer    │
│  broadcasts to    │
│  user's room      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  WebSocket sends  │
│  update to client │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Frontend updates │
│  component state  │
└───────────────────┘
```

### 3. Settlement Flow

```
User Clicks "Withdraw"
        │
        ▼
┌───────────────────┐
│  POST /settlements│
│  /withdraw/       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  SettlementViewSet│
│  - Check balance  │
│  - Validate user  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Calculate        │
│  available balance│
│  (7+ days old)    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Create Settlement│
│  record in DB     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Trigger payment  │
│  processor        │
│  (Future: Stripe) │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Return success   │
│  response         │
└───────────────────┘
```

## Component Architecture

### Frontend Component Tree

```
DashboardPage
├── Header
│   ├── Title
│   └── WebSocket Status Indicator
│
├── Metrics Grid (4 cards)
│   ├── Total Transactions
│   ├── Total Volume
│   ├── Success Rate
│   └── Average Transaction
│
├── Charts Grid (2 columns)
│   ├── Daily Volume Chart (AreaChart)
│   └── Provider Distribution (BarChart)
│
├── Status Distribution
│   └── Status Cards Grid
│
├── RecentTransactions
│   ├── Table Header
│   └── Transaction Rows
│       ├── Reference
│       ├── Customer
│       ├── Amount
│       ├── Provider
│       ├── Status Badge
│       └── Timestamp
│
├── Bottom Grid (2x2)
│   ├── ActivityFeed
│   │   ├── Live Indicator
│   │   └── Event List
│   │       ├── Transaction Events
│   │       ├── Webhook Events
│   │       └── Settlement Events
│   │
│   ├── SettlementSummary
│   │   ├── Available Balance
│   │   ├── Pending Balance
│   │   ├── Next Settlement Date
│   │   └── Withdraw Button
│   │
│   ├── SystemHealth
│   │   ├── Webhook Delivery Rate
│   │   ├── System Uptime
│   │   ├── Response Time
│   │   └── Request Stats
│   │
│   └── UserSummary
│       ├── Avatar
│       ├── User Info
│       ├── Company Details
│       ├── KYC Status
│       └── Account Type
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                        Users Table                           │
│  - id (PK)                                                   │
│  - email                                                     │
│  - password_hash                                             │
│  - created_at                                                │
└────────────┬────────────────────────────────────────────────┘
             │
             │ 1:N
             │
┌────────────▼────────────────────────────────────────────────┐
│                    Transactions Table                        │
│  - id (PK)                                                   │
│  - user_id (FK)                                              │
│  - reference (unique)                                        │
│  - amount                                                    │
│  - currency                                                  │
│  - status                                                    │
│  - provider                                                  │
│  - customer_email                                            │
│  - fee                                                       │
│  - net_amount                                                │
│  - created_at                                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Settlements Table                         │
│  - id (PK)                                                   │
│  - user_id (FK)                                              │
│  - amount                                                    │
│  - currency                                                  │
│  - status                                                    │
│  - reference (unique)                                        │
│  - bank_account                                              │
│  - created_at                                                │
│  - completed_at                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      API Logs Table                          │
│  - id (PK)                                                   │
│  - user_id (FK)                                              │
│  - endpoint                                                  │
│  - method                                                    │
│  - status_code                                               │
│  - response_time                                             │
│  - created_at                                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Webhooks Table                           │
│  - id (PK)                                                   │
│  - user_id (FK)                                              │
│  - url                                                       │
│  - event_types                                               │
│  - is_active                                                 │
│  - last_triggered                                            │
│  - created_at                                                │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                                                              │
│  Framework:     Next.js 16 (React 19)                       │
│  Language:      TypeScript                                  │
│  Styling:       Tailwind CSS                                │
│  Charts:        Recharts                                    │
│  UI Components: Radix UI                                    │
│  State:         React Hooks                                 │
│  API Client:    Fetch API + Custom Wrappers                │
│  WebSocket:     Native WebSocket API                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
│                                                              │
│  Framework:     Django 4.2                                  │
│  Language:      Python 3.10+                                │
│  API:           Django REST Framework                       │
│  GraphQL:       Graphene-Django                             │
│  WebSocket:     Django Channels                             │
│  Auth:          JWT (Simple JWT)                            │
│  ASGI Server:   Daphne                                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│                                                              │
│  Database:      PostgreSQL                                  │
│  Cache:         Redis                                       │
│  Channel Layer: Redis (for WebSocket)                       │
│  ORM:           Django ORM                                  │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CDN                                  │
│                    (Vercel Edge)                             │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Vercel)                          │
│                   - Next.js App                              │
│                   - Static Assets                            │
│                   - API Routes                               │
└────────────┬────────────────────────────────────────────────┘
             │
             │ HTTPS/WSS
             │
┌────────────▼────────────────────────────────────────────────┐
│                   Load Balancer                              │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Render/Railway/AWS)                    │
│              - Django ASGI App                               │
│              - Daphne Server                                 │
│              - WebSocket Support                             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┐
             │              │              │
             ▼              ▼              ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   PostgreSQL     │ │    Redis     │ │   Storage    │
│   (Database)     │ │   (Cache)    │ │   (S3/etc)   │
└──────────────────┘ └──────────────┘ └──────────────┘
```

---

**This architecture provides**:
- ✅ Real-time updates via WebSocket
- ✅ Flexible data fetching (GraphQL + REST)
- ✅ Scalable backend with ASGI
- ✅ Fast frontend with Next.js
- ✅ Reliable data storage
- ✅ Production-ready deployment
