# PayBridge Deployment Guide

## Overview

PayBridge consists of two main components:
1. **Frontend** - Next.js application (Node.js)
2. **Backend** - Django REST API (Python)

Both can be deployed separately to different services.

## Prerequisites

- A database (PostgreSQL recommended)
- Redis instance (for caching and Celery)
- Payment provider accounts (Paystack, Flutterwave, etc.)
- Domain names for both frontend and backend
- SSL certificates

## Backend Deployment

### Option 1: Render.com (Recommended)

1. Create Render account
2. Create PostgreSQL database
3. Create Redis instance
4. Create Web Service:
   - Repository: Your GitHub repo
   - Root Directory: `backend`
   - Environment: Python
   - Build Command: `pip install -r requirements.txt && python manage.py migrate`
   - Start Command: `gunicorn paybridge.wsgi:application`

5. Add environment variables:
   \`\`\`
   SECRET_KEY=your-secret-key
   DEBUG=False
   DATABASE_URL=provided-by-render
   REDIS_URL=provided-by-render
   PAYSTACK_PUBLIC_KEY=your-key
   PAYSTACK_SECRET_KEY=your-key
   # ... other provider keys
   \`\`\`

6. Deploy!

### Option 2: Railway.app

1. Create Railway account
2. Connect GitHub repository
3. Create PostgreSQL database plugin
4. Create Redis plugin
5. Create Python service from root directory
6. Configure environment variables
7. Deploy!

### Option 3: AWS EC2

1. Create EC2 instance (Ubuntu 22.04)
2. Install dependencies:
   \`\`\`bash
   sudo apt-get update
   sudo apt-get install python3.10 python3.10-venv postgresql postgresql-contrib redis-server nginx
   \`\`\`

3. Clone repository
4. Create virtual environment and install dependencies
5. Configure environment variables
6. Run migrations
7. Create systemd service file:
   \`\`\`ini
   [Unit]
   Description=PayBridge Django API
   After=network.target

   [Service]
   Type=notify
   User=www-data
   WorkingDirectory=/app/backend
   ExecStart=/app/venv/bin/gunicorn paybridge.wsgi --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   \`\`\`

8. Configure Nginx as reverse proxy
9. Set up SSL with Certbot

## Frontend Deployment

### Option 1: Vercel (Recommended for Next.js)

1. Create Vercel account
2. Connect GitHub repository
3. Select `frontend` directory as root
4. Add environment variable:
   \`\`\`
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain/api/v1
   \`\`\`
5. Deploy!

### Option 2: Netlify

1. Create Netlify account
2. Connect GitHub repository
3. Build settings:
   - Build command: `npm run build`
   - Publish directory: `.next`

4. Add environment variables
5. Deploy!

### Option 3: Docker + AWS ECS

1. Create Dockerfile for Next.js
2. Push image to ECR
3. Create ECS task definition
4. Deploy to ECS cluster

## Environment Variables

### Backend (.env)
\`\`\`env
# Django
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com,localhost

# Database
DATABASE_URL=postgresql://user:password@host:5432/paybridge

# Redis/Celery
REDIS_URL=redis://host:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Paystack
PAYSTACK_PUBLIC_KEY=pk_live_xxxx
PAYSTACK_SECRET_KEY=sk_live_xxxx

# Flutterwave
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_LIVE_xxxx
FLUTTERWAVE_SECRET_KEY=FLWSECK_LIVE_xxxx

# Stripe
STRIPE_API_KEY=sk_live_xxxx
STRIPE_WEBHOOK_SECRET=whsec_live_xxxx

# Other providers
MONO_API_KEY=mono_live_xxxx
OKRA_API_KEY=okra_live_xxxx
CHAPA_API_KEY=CHASECK_LIVE_xxxx
LAZERPAY_PUBLIC_KEY=pk_live_xxxx
LAZERPAY_SECRET_KEY=sk_live_xxxx
\`\`\`

### Frontend (.env.local)
\`\`\`env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com/api/v1
\`\`\`

## Database Migrations

Run migrations on deployment:

\`\`\`bash
# On Railway, Render, or EC2 (before app starts)
python manage.py migrate

# Or in your deployment pipeline
\`\`\`

## SSL/HTTPS

### Using Certbot (for EC2)
\`\`\`bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d api.yourdomain.com
\`\`\`

### Auto-renewal
\`\`\`bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
\`\`\`

## Monitoring

### Backend
- Use Sentry for error tracking
- Set up CloudWatch or DataDog for monitoring
- Enable Django logging

### Frontend
- Use Vercel analytics
- Set up error tracking (Sentry)

## Backup Strategy

- Database: Daily automated backups
- Redis: Persist AOF or RDB snapshots
- Code: Git repository is your backup

## Troubleshooting

### 502 Bad Gateway
- Check if backend is running
- Verify environment variables
- Check logs with: `journalctl -u paybridge-api`

### Database connection errors
- Verify DATABASE_URL
- Check database is running and accessible
- Ensure firewall allows connections

### Payment webhooks not working
- Verify webhook URL in payment provider dashboard
- Check CORS configuration
- Verify webhook secret tokens

## Post-Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Change SECRET_KEY to production value
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up SSL certificates
- [ ] Configure payment provider webhooks
- [ ] Test payment flow end-to-end
- [ ] Set up monitoring and alerts
- [ ] Enable HTTPS redirect
- [ ] Configure CORS properly
- [ ] Test email functionality
- [ ] Set up database backups
- [ ] Create admin user
- [ ] Review security settings
