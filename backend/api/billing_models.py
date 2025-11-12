"""
Billing and Subscription Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid
from datetime import timedelta


class Plan(models.Model):
    """Subscription plans with features and limits"""
    PLAN_TIER_CHOICES = (
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('growth', 'Growth'),
        ('enterprise', 'Enterprise'),
    )
    
    DURATION_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    tier = models.CharField(max_length=20, choices=PLAN_TIER_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='monthly')
    duration_days = models.IntegerField(default=30)  # For calculating renewal
    
    # Limits
    api_limit = models.IntegerField(help_text="API calls per month")
    webhook_limit = models.IntegerField(default=1)
    
    # Feature flags
    has_analytics = models.BooleanField(default=False)
    analytics_level = models.CharField(max_length=20, default='none')  # none, basic, advanced
    has_priority_support = models.BooleanField(default=False)
    has_custom_branding = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_plans'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.duration}"


class Feature(models.Model):
    """Features that can be assigned to plans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    plan_tier_access = models.JSONField(default=list)  # ['starter', 'growth', 'enterprise']
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_features'
    
    def __str__(self):
        return self.name
    
    def is_available_for_plan(self, plan_tier):
        """Check if feature is available for a plan tier"""
        return plan_tier in self.plan_tier_access


class BillingSubscription(models.Model):
    """User subscriptions to plans"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('past_due', 'Past Due'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    start_date = models.DateTimeField(default=timezone.now)
    renewal_date = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Provider-specific IDs
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    paystack_subscription_code = models.CharField(max_length=255, blank=True)
    flutterwave_subscription_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_subscriptions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['renewal_date']),
        ]
    
    def save(self, *args, **kwargs):
        # Set renewal date if not set
        if not self.renewal_date:
            self.renewal_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    def is_expired(self):
        """Check if subscription is expired"""
        return timezone.now() > self.renewal_date
    
    def days_until_renewal(self):
        """Get days until renewal"""
        delta = self.renewal_date - timezone.now()
        return max(0, delta.days)


class Payment(models.Model):
    """Payment records for subscriptions"""
    PROVIDER_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('stripe', 'Stripe'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billing_payments')
    subscription = models.ForeignKey(BillingSubscription, on_delete=models.SET_NULL, null=True, related_name='payments')
    
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True)
    payment_intent = models.CharField(max_length=255, unique=True, db_index=True)
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'billing_payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['payment_intent']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.status}"


class PaymentAttempt(models.Model):
    """Track payment retry attempts"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(BillingSubscription, on_delete=models.CASCADE, related_name='payment_attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_attempts')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, related_name='attempts')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempt_number = models.IntegerField(default=1)
    
    provider_reference = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=255, db_index=True)
    
    retry_scheduled_for = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_payment_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', '-created_at']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['retry_scheduled_for']),
        ]
    
    def __str__(self):
        return f"Attempt {self.attempt_number} - {self.user.email} - {self.status}"


class UsageTracking(models.Model):
    """Track real-time usage for plan limits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_tracking')
    subscription = models.ForeignKey(BillingSubscription, on_delete=models.CASCADE, related_name='usage_records')
    
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Usage counters
    api_calls_used = models.IntegerField(default=0)
    webhooks_used = models.IntegerField(default=0)
    analytics_requests = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_usage_tracking'
        unique_together = ('user', 'period_start', 'period_end')
        indexes = [
            models.Index(fields=['user', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.period_start.date()} to {self.period_end.date()}"
    
    def get_api_calls_remaining(self):
        """Get remaining API calls"""
        return max(0, self.subscription.plan.api_limit - self.api_calls_used)
    
    def is_api_limit_reached(self):
        """Check if API limit is reached"""
        return self.api_calls_used >= self.subscription.plan.api_limit
