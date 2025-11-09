from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid
import secrets

# Common currency choices used across models
CURRENCY_CHOICES = (
    ('NGN', 'Nigerian Naira'),
    ('GHS', 'Ghanaian Cedi'),
    ('KES', 'Kenyan Shilling'),
    ('UGX', 'Ugandan Shilling'),
    ('TZS', 'Tanzanian Shilling'),
    ('ETB', 'Ethiopian Birr'),
    ('ZAR', 'South African Rand'),
    ('USD', 'US Dollar'),
    ('GBP', 'British Pound'),
    ('EUR', 'Euro'),
)

class UserProfile(models.Model):
    COUNTRY_CHOICES = (
        ('NG', 'Nigeria'),
        ('GH', 'Ghana'),
        ('KE', 'Kenya'),
        ('UG', 'Uganda'),
        ('TZ', 'Tanzania'),
        ('ET', 'Ethiopia'),
        ('ZA', 'South Africa'),
        ('US', 'United States'),
        ('GB', 'United Kingdom'),
        ('CA', 'Canada'),
    )
    
    DEVELOPER_TYPE_CHOICES = (
        ('individual', 'Individual Developer'),
        ('startup', 'Startup'),
        ('enterprise', 'Enterprise'),
        ('agency', 'Agency'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='NG')
    phone_number = models.CharField(max_length=20, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    developer_type = models.CharField(max_length=20, choices=DEVELOPER_TYPE_CHOICES, blank=True)
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    kyc_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.email} - {self.company_name}"


class APIKey(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('revoked', 'Revoked'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True, db_index=True)
    secret = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    last_used = models.DateTimeField(null=True, blank=True)
    ip_whitelist = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = f"pk_{secrets.token_urlsafe(32)}"
        if not self.secret:
            self.secret = secrets.token_urlsafe(64)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class PaymentProvider(models.Model):
    PROVIDER_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('stripe', 'Stripe'),
        ('mono', 'Mono'),
        ('okra', 'Okra'),
        ('chapa', 'Chapa'),
        ('lazerpay', 'Lazerpay'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    public_key = models.CharField(max_length=500)
    secret_key = models.CharField(max_length=500)
    is_live = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_providers'
        unique_together = ('user', 'provider')
    
    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, related_name='transactions')
    provider = models.CharField(max_length=20, choices=PaymentProvider.PROVIDER_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NGN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=255, unique=True, db_index=True)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    provider_response = models.JSONField(default=dict, blank=True)
    settlement = models.ForeignKey('Settlement', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)  # For tokenized payments only
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reference']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def calculate_fee(self):
        from decimal import Decimal
        self.fee = self.amount * Decimal(str(2.5 / 100))
        self.net_amount = self.amount - self.fee
        return self.net_amount
    
    def __str__(self):
        return f"{self.reference} - {self.amount} {self.currency}"


class Webhook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    url = models.URLField()
    event_types = models.JSONField(default=list)  # ['payment.completed', 'payment.failed', etc]
    is_active = models.BooleanField(default=True)
    secret = models.CharField(max_length=255, unique=True)
    retry_count = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhooks'
    
    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = secrets.token_urlsafe(64)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.url}"


class Subscription(models.Model):
    PLAN_CHOICES = (
        ('starter', 'Starter'),
        ('growth', 'Growth'),
        ('enterprise', 'Enterprise'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    renewal_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan}"


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create_api_key', 'Create API Key'),
        ('revoke_api_key', 'Revoke API Key'),
        ('update_profile', 'Update Profile'),
        ('create_webhook', 'Create Webhook'),
        ('delete_webhook', 'Delete Webhook'),
        ('update_payment_provider', 'Update Payment Provider'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action}"


class KYCVerification(models.Model):
    VERIFICATION_TYPE_CHOICES = (
        ('bvn', 'Bank Verification Number'),
        ('nin', 'National Identification Number'),
        ('account', 'Account Verification'),
    )
    
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_verifications')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES)
    verification_id = models.CharField(max_length=255)  # BVN, NIN, or account number
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    provider = models.CharField(max_length=20)  # 'mono' or 'okra'
    provider_reference = models.CharField(max_length=255, unique=True)
    verification_data = models.JSONField(default=dict)  # Response from provider
    error_message = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kyc_verifications'
        unique_together = ('user', 'verification_type')
    
    def __str__(self):
        return f"{self.user.email} - {self.verification_type}"


class APILog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_logs')
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, related_name='logs')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # milliseconds
    request_size = models.BigIntegerField(default=0)  # bytes
    response_size = models.BigIntegerField(default=0)  # bytes
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'api_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['api_key', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.endpoint}"


class BillingPlan(models.Model):
    BILLING_TYPE_CHOICES = (
        ('subscription', 'Subscription'),
        ('pay_per_call', 'Pay Per Call'),
    )
    
    name = models.CharField(max_length=100)
    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    api_calls_limit = models.IntegerField(null=True, blank=True)  # None = unlimited
    transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    per_call_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    features = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'billing_plans'
    
    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}"


class UsageMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_metrics')
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    api_calls = models.BigIntegerField(default=0)
    transaction_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    data_transferred_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'usage_metrics'
        unique_together = ('user', 'period_start', 'period_end')
    
    def __str__(self):
        return f"{self.user.email} - {self.period_start} to {self.period_end}"


class WebhookEvent(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    attempt = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.webhook.url} - {self.event_type}"


class Settlement(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settlements')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='NGN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    bank_account = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'settlements'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"STL-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency}"
