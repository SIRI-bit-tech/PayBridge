from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from .models import Invoice, UsageMetric, APILog, Transaction, BillingPlan, Subscription
import logging

logger = logging.getLogger(__name__)


class BillingService:
    """Billing and usage tracking service"""
    
    @staticmethod
    def record_api_usage(api_key, endpoint, status_code, response_time):
        """Record API usage for billing purposes"""
        # This is called via middleware/signals
        pass
    
    @staticmethod
    def calculate_monthly_usage(user, billing_period_start, billing_period_end):
        """Calculate monthly usage metrics"""
        api_logs = APILog.objects.filter(
            user=user,
            created_at__gte=billing_period_start,
            created_at__lte=billing_period_end
        )
        
        transactions = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__gte=billing_period_start,
            created_at__lte=billing_period_end
        )
        
        # Calculate totals
        api_calls = api_logs.count()
        transaction_volume = float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0)
        data_transferred = float(api_logs.aggregate(Sum('request_size'), Sum('response_size')).get('request_size__sum', 0) or 0)
        
        return {
            'api_calls': api_calls,
            'transaction_volume': transaction_volume,
            'data_transferred_mb': data_transferred / (1024 * 1024),
        }
    
    @staticmethod
    def generate_invoice(user, billing_period_start, billing_period_end):
        """Generate invoice for a billing period"""
        subscription = user.subscription
        plan = subscription.plan
        
        # Calculate usage
        usage = BillingService.calculate_monthly_usage(user, billing_period_start, billing_period_end)
        
        # Get plan details
        billing_plan = BillingPlan.objects.filter(name__icontains=plan).first()
        
        # Calculate charges
        base_charge = Decimal(str(billing_plan.monthly_price)) if billing_plan else Decimal('0')
        
        # Add per-call overage charges if applicable
        overage_charge = Decimal('0')
        if billing_plan and billing_plan.api_calls_limit:
            if usage['api_calls'] > billing_plan.api_calls_limit:
                overage_calls = usage['api_calls'] - billing_plan.api_calls_limit
                overage_charge = Decimal(str(overage_calls)) * Decimal(str(billing_plan.per_call_cost))
        
        total_amount = base_charge + overage_charge
        tax = total_amount * Decimal('0.1')  # 10% tax
        grand_total = total_amount + tax
        
        # Create invoice
        from datetime import datetime
        invoice_number = f"INV-{user.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        invoice = Invoice.objects.create(
            user=user,
            subscription=subscription,
            invoice_number=invoice_number,
            amount=total_amount,
            tax=tax,
            total=grand_total,
            due_date=timezone.now().date() + timedelta(days=30),
            status='issued'
        )
        
        # Create usage metric record
        UsageMetric.objects.create(
            user=user,
            period_start=billing_period_start,
            period_end=billing_period_end,
            api_calls=usage['api_calls'],
            transaction_volume=Decimal(str(usage['transaction_volume'])),
            data_transferred_mb=Decimal(str(usage['data_transferred_mb'])),
            cost=total_amount
        )
        
        logger.info(f"Invoice {invoice_number} generated for user {user.email}")
        return invoice
    
    @staticmethod
    def mark_invoice_paid(invoice_id, payment_method='stripe'):
        """Mark invoice as paid"""
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.status = 'paid'
        invoice.paid_date = timezone.now().date()
        invoice.payment_method = payment_method
        invoice.save()
        
        logger.info(f"Invoice {invoice.invoice_number} marked as paid")
        return invoice
