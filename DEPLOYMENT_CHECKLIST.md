# PayBridge Deployment Checklist

## Pre-Deployment (Local Testing)

- [ ] Clone repository
- [ ] Backend: Install dependencies (`pip install -r requirements.txt`)
- [ ] Backend: Create PostgreSQL database
- [ ] Backend: Configure `.env` with test credentials
- [ ] Backend: Run migrations (`python manage.py migrate`)
- [ ] Backend: Create superuser (`python manage.py createsuperuser`)
- [ ] Backend: Run development server (`python manage.py runserver`)
- [ ] Frontend: Install dependencies (`npm install`)
- [ ] Frontend: Configure `.env.local` with local API URL
- [ ] Frontend: Run development server (`npm run dev`)
- [ ] Test complete user flow: signup → login → create API key → configure provider
- [ ] Test payment initiation and verification

## Payment Provider Setup

### Paystack
- [ ] Create Paystack account (paystack.com)
- [ ] Get test API keys from Settings → API Keys & Webhooks
- [ ] Add to `.env`:
  - `PAYSTACK_PUBLIC_KEY=pk_test_xxxxx`
  - `PAYSTACK_SECRET_KEY=sk_test_xxxxx`
- [ ] Configure webhook in Paystack: `http://localhost:8000/api/v1/webhooks/paystack/`
- [ ] Test: Create transaction and verify webhook fires

### Flutterwave
- [ ] Create Flutterwave account (dashboard.flutterwave.com)
- [ ] Get test API keys from Settings → API Keys
- [ ] Add to `.env`:
  - `FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST_xxxxx`
  - `FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST_xxxxx`
- [ ] Configure webhook in Flutterwave dashboard
- [ ] Test integration

### Stripe
- [ ] Create Stripe account (stripe.com)
- [ ] Get test API keys from Developers → API Keys
- [ ] Add to `.env`:
  - `STRIPE_API_KEY=sk_test_xxxxx`
  - `STRIPE_WEBHOOK_SECRET=whsec_test_xxxxx`
- [ ] Configure webhook endpoint
- [ ] Test integration

### Other Providers (Mono, Okra, Chapa, Lazerpay)
- [ ] Repeat similar process for each provider
- [ ] Store all credentials securely

## Production Infrastructure Setup

### Database (PostgreSQL)

#### Option A: Render.com PostgreSQL
- [ ] Create Render account
- [ ] Create PostgreSQL database
- [ ] Note the connection URL
- [ ] Enable backups (automatic)

#### Option B: AWS RDS
- [ ] Create RDS instance
- [ ] Set security groups to allow connections
- [ ] Create master user
- [ ] Note connection details

#### Option C: Your Own Server
- [ ] Install PostgreSQL
- [ ] Create database and user
- [ ] Set strong password
- [ ] Configure backups

### Redis (Cache & Celery)

#### Option A: Render.com Redis
- [ ] Create Redis instance on Render
- [ ] Note the connection URL

#### Option B: AWS ElastiCache
- [ ] Create ElastiCache instance
- [ ] Configure security group

#### Option C: Your Own Server
- [ ] Install Redis
- [ ] Start Redis server
- [ ] Configure persistence

## Backend Deployment (Choose One)

### Deployment to Render.com (Recommended)

1. **Prepare Code**
   - [ ] Push code to GitHub
   - [ ] Create `render.yaml` for infrastructure as code
   - [ ] Update `requirements.txt` (already done)

2. **Create Database**
   - [ ] On Render, create PostgreSQL database
   - [ ] Copy connection string to clipboard

3. **Create Redis**
   - [ ] On Render, create Redis instance
   - [ ] Copy connection URL

4. **Create Web Service**
   - [ ] Click "Create New" → "Web Service"
   - [ ] Connect GitHub repository
   - [ ] Select branch (main)
   - [ ] Set name: `paybridge-api`
   - [ ] Select root directory: `backend`
   - [ ] Environment: Python
   - [ ] Build command:
     \`\`\`
     pip install -r requirements.txt && python manage.py migrate
     \`\`\`
   - [ ] Start command:
     \`\`\`
     gunicorn paybridge.wsgi:application
     \`\`\`

5. **Add Environment Variables**
   - [ ] `SECRET_KEY` - Generate secure random value
   - [ ] `DEBUG=False`
   - [ ] `ALLOWED_HOSTS=api.yourdomain.com`
   - [ ] `DATABASE_URL` - From PostgreSQL instance
   - [ ] `REDIS_URL` - From Redis instance
   - [ ] `EMAIL_*` - Email provider credentials
   - [ ] `PAYSTACK_*` - **LIVE** Paystack keys
   - [ ] `FLUTTERWAVE_*` - **LIVE** Flutterwave keys
   - [ ] `STRIPE_*` - **LIVE** Stripe keys
   - [ ] All other payment provider keys
   - [ ] `CORS_ALLOWED_ORIGINS` - Your frontend domain

6. **Deploy**
   - [ ] Click "Deploy"
   - [ ] Monitor deployment logs
   - [ ] Verify successful deployment

### Deployment to Railway.app

1. **Create Account**
   - [ ] Sign up at railway.app

2. **Connect GitHub**
   - [ ] Link your GitHub repository

3. **Create Services**
   - [ ] Create PostgreSQL plugin
   - [ ] Create Redis plugin
   - [ ] Create Python service from `backend` directory

4. **Configure**
   - [ ] Add all environment variables
   - [ ] Set build command
   - [ ] Set start command

5. **Deploy**
   - [ ] Push code
   - [ ] Railway auto-deploys

### Deployment to AWS EC2

1. **Launch Instance**
   - [ ] Create EC2 instance (Ubuntu 22.04, t2.small minimum)
   - [ ] Security group: Allow SSH (22), HTTP (80), HTTPS (443)

2. **Install Software**
   - [ ] SSH into instance
   - [ ] Install Python 3.10: `sudo apt-get install python3.10 python3.10-venv`
   - [ ] Install PostgreSQL: `sudo apt-get install postgresql postgresql-contrib`
   - [ ] Install Redis: `sudo apt-get install redis-server`
   - [ ] Install Nginx: `sudo apt-get install nginx`
   - [ ] Install Git: `sudo apt-get install git`

3. **Clone & Setup**
   - [ ] Clone repository
   - [ ] Create virtual environment
   - [ ] Install dependencies
   - [ ] Configure `.env` file

4. **Create Systemd Service**
   - [ ] Create `/etc/systemd/system/paybridge.service`
   - [ ] Enable and start service

5. **Configure Nginx**
   - [ ] Create `/etc/nginx/sites-available/paybridge`
   - [ ] Enable site
   - [ ] Restart Nginx

6. **SSL Certificate**
   - [ ] Install Certbot: `sudo apt-get install certbot python3-certbot-nginx`
   - [ ] Run: `sudo certbot certonly --nginx -d api.yourdomain.com`

## Frontend Deployment (Vercel - Recommended)

1. **Create Vercel Account**
   - [ ] Sign up at vercel.com
   - [ ] Connect GitHub account

2. **Import Project**
   - [ ] Click "Import Project"
   - [ ] Select your PayBridge GitHub repository
   - [ ] Select `frontend` directory as root
   - [ ] Vercel detects Next.js automatically

3. **Configure Environment**
   - [ ] Set environment variable:
     - Key: `NEXT_PUBLIC_API_BASE_URL`
     - Value: `https://api.yourdomain.com/api/v1`

4. **Deploy**
   - [ ] Click "Deploy"
   - [ ] Wait for deployment to complete
   - [ ] Visit your frontend URL

### Alternative: Netlify

1. **Create Account**
   - [ ] Sign up at netlify.com

2. **Connect GitHub**
   - [ ] Authorize Netlify

3. **Deploy**
   - [ ] Select repository
   - [ ] Deploy settings:
     - Base directory: `frontend`
     - Build command: `npm run build`
     - Publish directory: `.next`

4. **Configure**
   - [ ] Add environment variables

## Payment Provider Configuration (Production)

### Update All Provider Credentials to LIVE keys

#### Paystack
- [ ] Go to Paystack Settings → API Keys & Webhooks
- [ ] Get LIVE Public Key: `pk_live_xxxxx`
- [ ] Get LIVE Secret Key: `sk_live_xxxxx`
- [ ] Add Webhook URL: `https://api.yourdomain.com/api/v1/webhooks/paystack/`
- [ ] Update backend environment variables
- [ ] Test with real transaction

#### Flutterwave
- [ ] Go to Flutterwave Settings → API Keys
- [ ] Get LIVE keys
- [ ] Add Webhook URL in dashboard
- [ ] Update environment variables

#### Stripe
- [ ] Go to Stripe Developers → API Keys
- [ ] Get LIVE Secret Key
- [ ] Create Webhook Endpoint: `https://api.yourdomain.com/api/v1/webhooks/stripe/`
- [ ] Copy Signing Secret
- [ ] Update environment variables

#### Other Providers
- [ ] Repeat similar process for Mono, Okra, Chapa, Lazerpay
- [ ] Update all LIVE credentials

## Domain & SSL Setup

- [ ] Register domain (yourdomain.com)
- [ ] Configure DNS:
  - [ ] `api.yourdomain.com` → Backend provider (Render, Railway, etc.)
  - [ ] `app.yourdomain.com` → Vercel (if using custom domain)
- [ ] Set up SSL certificates (auto with Render/Vercel/Railway)
- [ ] Update ALLOWED_HOSTS in backend `.env`
- [ ] Update CORS origins in backend
- [ ] Update frontend API URL

## Testing (Production)

### Smoke Tests
- [ ] Frontend loads at https://app.yourdomain.com
- [ ] Can access login page
- [ ] Can create account
- [ ] Can login
- [ ] Dashboard loads with statistics

### API Tests
- [ ] Can obtain JWT token: `POST /api/v1/auth/token/`
- [ ] Can access profile: `GET /api/v1/profile/me/`
- [ ] Can create API key: `POST /api/v1/api-keys/`
- [ ] Can configure payment provider

### Payment Flow Tests
- [ ] Can initiate test transaction
- [ ] Can verify payment status
- [ ] Webhook fires on payment completion
- [ ] Transaction appears in dashboard

### Provider Tests
- [ ] Test Paystack payment
- [ ] Test Flutterwave payment
- [ ] Test Stripe payment
- [ ] Verify webhooks for each provider

## Post-Deployment Configuration

### Monitoring & Alerts
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Configure log aggregation (e.g., Papertrail)
- [ ] Set up email alerts for errors

### Backups
- [ ] Enable automatic database backups (Render does this automatically)
- [ ] Verify backup retention policy
- [ ] Test backup restoration

### Security
- [ ] Review CORS settings
- [ ] Review ALLOWED_HOSTS
- [ ] Verify HTTPS is enforced
- [ ] Check secret keys are not in logs
- [ ] Enable rate limiting (if needed)

### Documentation
- [ ] Update README with production URLs
- [ ] Document API endpoints
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedure

## Ongoing Maintenance

### Weekly
- [ ] Check error logs
- [ ] Monitor API response times
- [ ] Verify webhook delivery

### Monthly
- [ ] Review transaction statistics
- [ ] Check database size
- [ ] Update dependencies
- [ ] Review security logs

### Quarterly
- [ ] Full security audit
- [ ] Load testing
- [ ] Backup restoration test
- [ ] Disaster recovery drill

## Rollback Plan

If issues occur:
1. [ ] Revert to previous working version
2. [ ] Restore database from backup
3. [ ] Clear Redis cache
4. [ ] Test thoroughly
5. [ ] Monitor for 24 hours

## Success Indicators

- [ ] Frontend loads in <2 seconds
- [ ] API responds in <200ms
- [ ] 99.9% uptime
- [ ] Zero payment failures due to system issues
- [ ] Webhooks deliver within 30 seconds
- [ ] All logs are clean of errors

## Final Verification

- [ ] Can create user account
- [ ] Can create API key
- [ ] Can configure payment provider
- [ ] Can process payment through all providers
- [ ] All webhooks fire correctly
- [ ] Transaction history displays correctly
- [ ] No console errors in frontend
- [ ] No errors in backend logs
- [ ] Email notifications work (if configured)
- [ ] Audit logs capture all actions

---

## Support Contacts

- Paystack Support: https://paystack.com/support
- Flutterwave Support: https://twitter.com/Flutterwave
- Stripe Support: https://support.stripe.com
- Render Support: https://render.com/docs
- Vercel Support: https://vercel.com/support

---

**Congratulations! Your PayBridge deployment is complete!** 🎉

Start accepting payments across Africa now.
