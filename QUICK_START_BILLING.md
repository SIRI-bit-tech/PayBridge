# Quick Start Guide - Billing System

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
# Backend
cd backend
pip install redis aioredis

# Frontend (already has dependencies)
cd frontend
# npm install (if not done already)
```

### Step 2: Configure Environment (1 min)

Add to `backend/.env`:

```env
# Use test keys for development
PAYSTACK_SECRET_KEY=sk_test_your_key
PAYSTACK_PUBLIC_KEY=pk_test_your_key

FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-your_key
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-your_key
FLUTTERWAVE_SECRET_HASH=your_hash

STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

FRONTEND_URL=http://localhost:3000
```

### Step 3: Setup Database (2 min)

```bash
cd backend

# Create migrations for new billing models
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Initialize billing plans and features
python setup_billing.py
```

### Step 4: Start Services (1 min)

Open 6 terminals and run:

```bash
# Terminal 1: Django
cd backend
python manage.py runserver

# Terminal 2: Socket.IO Server
cd backend
python -m api.socketio_server

# Terminal 3: Celery Worker
cd backend
celery -A paybridge worker -l info

# Terminal 4: Celery Beat
cd backend
celery -A paybridge beat -l info

# Terminal 5: Redis
redis-server

# Terminal 6: Frontend
cd frontend
npm run dev
```

## ✅ Verify Installation

### 1. Check Plans Created

Visit: http://localhost:8000/admin/api/plan/

You should see 4 plans: Free, Starter, Growth, Enterprise

### 2. Check Frontend

Visit: http://localhost:3000/billing

You should see:
- Current plan (Free for new users)
- Usage statistics
- Available plans grid
- Real-time connection indicator

### 3. Test Real-Time Updates

Open browser console and watch for:
```
Billing Socket.IO connected
Joined billing room: billing_1
```

## 🧪 Quick Test

### Test 1: View Billing Page

1. Login to your account
2. Navigate to `/billing`
3. See your Free plan and usage

### Test 2: Try Upgrade Flow

1. Click "Upgrade" on Starter plan
2. Provider selection modal appears
3. Select a provider
4. (In test mode, you'll get a test payment URL)

### Test 3: Check Usage Tracking

```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User
from api.usage_tracking_service import UsageTrackingService

user = User.objects.first()

# Increment API call
UsageTrackingService.increment_api_call(user)

# Check usage
usage = UsageTrackingService.get_current_usage(user)
print(usage)
```

## 📝 Common Issues

### Issue: Plans not showing

**Solution:**
```bash
python setup_billing.py
```

### Issue: Socket.IO not connecting

**Solution:**
- Check Redis is running: `redis-cli ping` (should return PONG)
- Check Socket.IO server is running on port 8001
- Check frontend `.env.local` has: `NEXT_PUBLIC_SOCKET_URL=http://localhost:8001`

### Issue: Migrations fail

**Solution:**
```bash
# Reset migrations (development only!)
python manage.py migrate api zero
python manage.py makemigrations
python manage.py migrate
python setup_billing.py
```

### Issue: Celery not starting

**Solution:**
- Check Redis is running
- Verify `CELERY_BROKER_URL` in settings
- Try: `celery -A paybridge worker -l debug`

## 🎯 What to Test

### ✅ Basic Features
- [ ] View billing page
- [ ] See current plan
- [ ] View usage statistics
- [ ] See available plans
- [ ] Click upgrade button
- [ ] Provider selection modal opens

### ✅ Real-Time Features
- [ ] Socket.IO connects (check console)
- [ ] Usage updates in real-time
- [ ] Plan changes reflect instantly

### ✅ API Endpoints
- [ ] GET /api/billing/plan/ - Returns subscription data
- [ ] GET /api/billing/usage/ - Returns usage data
- [ ] POST /api/billing/subscribe/ - Creates payment session

## 🔧 Development Tips

### View Redis Data

```bash
redis-cli
> KEYS usage:*
> HGETALL usage:1:2024-01
```

### Monitor Celery Tasks

```bash
# View active tasks
celery -A paybridge inspect active

# View scheduled tasks
celery -A paybridge inspect scheduled

# View registered tasks
celery -A paybridge inspect registered
```

### Check Socket.IO Connections

Look for in Django logs:
```
Client connected: <sid> (User: user@example.com)
Joined billing room: billing_1
```

### Test Webhooks Locally

1. Install ngrok: https://ngrok.com/
2. Run: `ngrok http 8000`
3. Copy the HTTPS URL
4. Configure in provider dashboard:
   - Paystack: https://your-url.ngrok.io/api/webhooks/paystack/
   - Flutterwave: https://your-url.ngrok.io/api/webhooks/flutterwave/
   - Stripe: https://your-url.ngrok.io/api/webhooks/stripe/

## 📚 Next Steps

1. **Read Full Documentation**: `BILLING_SYSTEM_README.md`
2. **Review Implementation**: `BILLING_IMPLEMENTATION_SUMMARY.md`
3. **Test Payment Flow**: Use provider test cards
4. **Customize Plans**: Edit in Django admin
5. **Add Features**: Extend the system

## 🎉 You're Ready!

Your billing system is now running with:
- ✅ 4 subscription tiers
- ✅ 3 payment providers
- ✅ Real-time updates
- ✅ Usage tracking
- ✅ Auto-renewal
- ✅ Beautiful UI

Start building! 🚀

---

**Need Help?**
- Check logs in Django console
- Check Celery worker output
- Check browser console for Socket.IO
- Review `BILLING_SYSTEM_README.md`
