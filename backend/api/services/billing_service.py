from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum, Count
from api.models import Invoice, UsageMetric, APILog, BillingPlan
import uuid


class BillingService:
    """Subscription and billing management"""
    
    @staticmethod
    def generate_invoice(user, period_start, period_end):
        """Generate invoice for billing period"""
        from api.models import Subscription
        
        period_start = datetime.fromisoformat(period_start)
        period_end = datetime.fromisoformat(period_end)
        
        subscription = Subscription.objects.filter(user=user).first()
        if not subscription:
            raise ValueError("No active subscription")
        
        # Calculate usage
        api_logs = APILog.objects.filter(
            user=user,
            created_at__gte=period_start,
            created_at__lte=period_end
        )
        
        api_call_count = api_logs.count()
        data_transferred_mb = api_logs.aggregate(Sum('response_size'))['response_size__sum'] or 0
        data_transferred_mb = float(data_transferred_mb) / 1024 / 1024
        
        # Get billing plan
        billing_plan = BillingPlan.objects.filter(name=subscription.plan.title()).first()
        
        # Calculate charges
        base_amount = billing_plan.monthly_price if billing_plan else Decimal('0')
        overage_charges = Decimal('0')
        
        if billing_plan and billing_plan.api_calls_limit and api_call_count > billing_plan.api_calls_limit:
            overage = api_call_count - billing_plan.api_calls_limit
            overage_charges = Decimal(str(overage)) * billing_plan.per_call_cost
        
        total_amount = base_amount + overage_charges
        tax = total_amount * Decimal('0.1')  # 10% tax
        invoice_total = total_amount + tax
        
        invoice = Invoice.objects.create(
            user=user,
            subscription=subscription,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            amount=total_amount,
            tax=tax,
            total=invoice_total,
            due_date=period_end + timedelta(days=14),
            status='issued'
        )
        
        # Create usage metric
        UsageMetric.objects.create(
            user=user,
            period_start=period_start,
            period_end=period_end,
            api_calls=api_call_count,
            data_transferred_mb=data_transferred_mb,
            cost=total_amount
        )
        
        return invoice
    
    @staticmethod
    def process_stripe_payment(user, amount, description):
        """Process payment via Stripe"""
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_API_KEY
        
        try:
            customer = stripe.Customer.create(
                email=user.email,
                description=user.get_full_name() or user.email
            )
            
            charge = stripe.Charge.create(
                amount=int(float(amount) * 100),  # Convert to cents
                currency='usd',
                customer=customer.id,
                description=description
            )
            
            return {
                'success': True,
                'charge_id': charge.id,
                'amount': amount
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
