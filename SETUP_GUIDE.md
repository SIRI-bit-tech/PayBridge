# PayBridge Complete Setup Guide

## Quick Start

This guide will help you get PayBridge running locally and deployed to production.

## Part 1: Local Development Setup

### Backend Setup

1. **Clone and navigate to backend**
   \`\`\`bash
   cd backend
   \`\`\`

2. **Create Python virtual environment**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Set up PostgreSQL database**
   \`\`\`bash
   createdb paybridge
   \`\`\`

5. **Configure environment**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your local settings
   \`\`\`

6. **Run migrations**
   \`\`\`bash
   python manage.py migrate
   \`\`\`

7. **Create superuser**
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

8. **Start development server**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

Backend is now running at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**
   \`\`\`bash
   cd frontend
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   npm install
   \`\`\`

3. **Create environment file**
   \`\`\`bash
   cp .env.example .env.local
   # Edit with local API URL
   \`\`\`

4. **Start development server**
   \`\`\`bash
   npm run dev
   \`\`\`

Frontend is now running at `http://localhost:3000`

## Part 2: Configure Payment Providers

### Paystack

1. Create account at https://paystack.com
2. Go to Settings → API Keys & Webhooks
3. Copy Public Key and Secret Key
4. Add to backend `.env`:
   \`\`\`
   PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
   PAYSTACK_SECRET_KEY=sk_test_xxxxx
   \`\`\`
5. In frontend, navigate to Payment Providers
6. Add credentials for Paystack

### Flutterwave

1. Create account at https://dashboard.flutterwave.com
2. Go to Settings → API Keys
3. Copy Public Key and Secret Key
4. Add to backend `.env`:
   \`\`\`
   FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST_xxxxx
   FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST_xxxxx
   \`\`\`

### Stripe

1. Create account at https://dashboard.stripe.com
2. Go to Developers → API Keys
3. Copy Publishable Key and Secret Key
4. Set up webhook endpoint for `http://localhost:8000/api/v1/webhooks/stripe/`
5. Copy Signing Secret
6. Add to backend `.env`:
   \`\`\`
   STRIPE_API_KEY=sk_test_xxxxx
   STRIPE_WEBHOOK_SECRET=whsec_test_xxxxx
   \`\`\`

### Other Providers

Repeat the same process for:
- **Mono** (mono.co)
- **Okra** (okra.ng)
- **Chapa** (chapa.co)
- **Lazerpay** (lazerpay.com)

## Part 3: Test Payment Flow

1. **Login to frontend** at http://localhost:3000
2. **Create API Key** in API Keys section
3. **Configure Payment Provider** in Payment Providers section
4. **Create Transaction** through the dashboard
5. **Verify Transaction** status

## Part 4: Deploy to Production

### Step 1: Prepare Backend

1. **Create production environment file**
   \`\`\`bash
   # On your production server
   nano .env.production
   \`\`\`

2. **Add production values**
   \`\`\`env
   SECRET_KEY=<generate-secure-random-key>
   DEBUG=False
   ALLOWED_HOSTS=api.yourdomain.com
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   # Add production payment provider keys
   \`\`\`

3. **Create production database**
   \`\`\`bash
   createdb paybridge_prod
   \`\`\`

4. **Run migrations**
   \`\`\`bash
   python manage.py migrate --settings=paybridge.settings.production
   \`\`\`

### Step 2: Deploy Backend (Render.com Example)

1. **Push code to GitHub**
   \`\`\`bash
   git add .
   git commit -m "Initial deployment"
   git push origin main
   \`\`\`

2. **Create Render account** at render.com

3. **Connect GitHub repository**

4. **Create PostgreSQL database**
   - Set database URL in environment

5. **Create Redis instance**
   - Set Redis URL in environment

6. **Create Web Service**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt && python manage.py migrate`
   - Start Command: `gunicorn paybridge.wsgi:application`

7. **Add environment variables** (all from .env.production)

8. **Deploy!**

### Step 3: Deploy Frontend (Vercel Example)

1. **Create Vercel account** at vercel.com

2. **Connect GitHub repository**

3. **Import project**
   - Select `frontend` directory

4. **Add environment variable**
   \`\`\`
   NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1
   \`\`\`

5. **Deploy!**

## Part 5: Configure Webhooks

### In Payment Provider Dashboards

Set webhook endpoints:

- **Paystack**: `https://api.yourdomain.com/api/v1/webhooks/paystack/`
- **Flutterwave**: `https://api.yourdomain.com/api/v1/webhooks/flutterwave/`
- **Stripe**: `https://api.yourdomain.com/api/v1/webhooks/stripe/`
- **Chapa**: `https://api.yourdomain.com/api/v1/webhooks/chapa/`

### In PayBridge Dashboard

1. Go to Webhooks section
2. Add your endpoint: `https://your-server.com/webhooks/paybridge`
3. Select events to subscribe to
4. Save

## Part 6: Testing

### Unit Tests

\`\`\`bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test
\`\`\`

### Integration Tests

1. Create a test transaction
2. Verify it appears in dashboard
3. Test payment provider integration
4. Verify webhook is triggered

## Security Checklist

- [ ] Change `SECRET_KEY` to unique, random value
- [ ] Set `DEBUG=False` in production
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set strong database password
- [ ] Enable database backups
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Set up API rate limiting
- [ ] Enable audit logging
- [ ] Test payment flow with test credentials
- [ ] Review webhook signatures
- [ ] Set up monitoring and alerts

## Troubleshooting

### Frontend can't connect to backend

**Solution**: 
- Check `NEXT_PUBLIC_API_BASE_URL` is correct
- Verify backend is running
- Check CORS configuration in Django settings

### Payment webhooks not firing

**Solution**:
- Verify webhook URL in payment provider dashboard
- Check webhook secret is correct
- Verify webhook endpoint is accessible
- Check server logs for errors

### Database connection errors

**Solution**:
- Verify DATABASE_URL format
- Check database is running
- Verify credentials
- Check firewall allows connections

### 502 Bad Gateway on Render

**Solution**:
- Check build command succeeded
- Verify all environment variables set
- Check log output for errors
- Ensure web service start command is correct

## Support Resources

- Django Documentation: https://docs.djangoproject.com/
- Next.js Documentation: https://nextjs.org/docs
- Paystack API: https://paystack.com/docs/api/
- Flutterwave API: https://developer.flutterwave.com/
- Stripe API: https://stripe.com/docs/api
- Render Deploy Guide: https://render.com/docs
- Vercel Deploy Guide: https://vercel.com/docs

## Next Steps

1. Customize branding and styling
2. Add email notifications
3. Set up analytics
4. Configure automated backups
5. Set up monitoring and alerts
6. Create API documentation
7. Add more payment providers
8. Implement additional features

---

**Congratulations!** Your PayBridge deployment is complete. Start accepting payments from across Africa!
