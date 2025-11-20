"""
Production-grade Webhook Models for PayBridge
Handles both incoming provider webhooks and outgoing client webhooks
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator
import uuid
import secrets
import hmac
import hashlib


class WebhookEvent(models.Model):
    """
    Stores incoming webhook events from payment/KYC providers
    Used for audit, replay, and idempotency
    """
    PROCESSING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
    )
    
    PROVIDER_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('stripe', 'Stripe'),
        ('mono', 'Mono'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, db_index=True)
    provider_event_id = models.CharField(max_length=255, unique=True, db_index=True)
    canonical_event_type = models.CharField(max_length=100, db_index=True)
    
    raw_payload = models.JSONField()
    signature_valid = models.BooleanField(default=False)
    
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending', db_index=True)
    processing_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_events'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['provider', '-received_at']),
            models.Index(fields=['canonical_event_type', '-received_at']),
            models.Index(fields=['processing_status', '-received_at']),
            models.Index(fields=['provider_event_id']),
        ]
    
    def __str__(self):
        return f"{self.provider} - {self.canonical_event_type} - {self.provider_event_id}"


class WebhookSubscription(models.Model):
    """
    Client webhook endpoints that receive PayBridge events
    Developers register these to get notified of events
    """
    DELIVERY_STATUS_CHOICES = (
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('failing', 'Failing'),
        ('disabled', 'Disabled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhook_subscriptions')
    
    url = models.URLField(validators=[URLValidator()])
    secret_key = models.CharField(max_length=255, unique=True)
    
    selected_events = models.JSONField(default=list)  # ['payment.completed', 'payment.failed', etc]
    active = models.BooleanField(default=True, db_index=True)
    
    last_delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='healthy')
    last_delivery_at = models.DateTimeField(null=True, blank=True)
    
    failure_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'active']),
            models.Index(fields=['active', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = f"whsec_{secrets.token_urlsafe(32)}"
        super().save(*args, **kwargs)
    
    def generate_signature(self, payload, timestamp):
        """Generate HMAC signature for outgoing webhook"""
        import json
        message = f"{timestamp}.{json.dumps(payload, sort_keys=True)}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def rotate_secret(self):
        """Rotate the webhook secret"""
        self.secret_key = f"whsec_{secrets.token_urlsafe(32)}"
        self.save(update_fields=['secret_key', 'updated_at'])
        return self.secret_key
    
    def __str__(self):
        return f"{self.user.email} - {self.url}"


class WebhookDeliveryLog(models.Model):
    """
    Tracks every delivery attempt to client webhooks
    Used for monitoring, debugging, and retry logic
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('dead_letter', 'Dead Letter'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name='delivery_logs')
    webhook_event = models.ForeignKey(WebhookEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='deliveries')
    
    event_id = models.UUIDField(db_index=True)  # For idempotency
    event_type = models.CharField(max_length=100)
    
    attempt_number = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    http_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)  # Truncated to 1000 chars
    latency_ms = models.IntegerField(null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_delivery_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook_subscription', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['event_id', 'webhook_subscription']),
            models.Index(fields=['next_retry_at']),
        ]
    
    def __str__(self):
        return f"Delivery {self.id} - Attempt {self.attempt_number} - {self.status}"


class WebhookDeliveryMetrics(models.Model):
    """
    Aggregated metrics for webhook delivery monitoring
    Updated periodically for dashboard display
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name='metrics')
    
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField()
    
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    retry_count = models.IntegerField(default=0)
    dead_letter_count = models.IntegerField(default=0)
    
    avg_latency_ms = models.FloatField(default=0)
    p95_latency_ms = models.FloatField(default=0)
    p99_latency_ms = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhook_delivery_metrics'
        unique_together = ('webhook_subscription', 'period_start')
        ordering = ['-period_start']
    
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_deliveries == 0:
            return 0.0
        return (self.successful_deliveries / self.total_deliveries) * 100
    
    def __str__(self):
        return f"{self.webhook_subscription.url} - {self.period_start.date()}"
