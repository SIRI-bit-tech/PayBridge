from django.contrib import admin
from .models import (
    UserProfile, APIKey, PaymentProvider, Transaction, AuditLog
)
from .billing_models import Plan, BillingSubscription, Payment, Feature
from .webhook_models import (
    WebhookEvent, WebhookSubscription, WebhookDeliveryLog, WebhookDeliveryMetrics
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'country', 'kyc_verified']
    search_fields = ['user__email', 'company_name']

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'status', 'created_at']
    search_fields = ['user__email', 'name']
    readonly_fields = ['key', 'secret', 'created_at']

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'is_live', 'is_active']
    search_fields = ['user__email', 'provider']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'amount', 'status', 'created_at']
    search_fields = ['reference', 'user__email']
    list_filter = ['status', 'provider', 'currency']

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['provider', 'canonical_event_type', 'provider_event_id', 'processing_status', 'received_at']
    search_fields = ['provider_event_id', 'canonical_event_type']
    list_filter = ['provider', 'processing_status', 'signature_valid']
    readonly_fields = ['id', 'raw_payload', 'received_at', 'created_at', 'updated_at']

@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'active', 'last_delivery_status', 'last_delivery_at']
    search_fields = ['user__email', 'url']
    list_filter = ['active', 'last_delivery_status']
    readonly_fields = ['secret_key', 'created_at', 'updated_at']

@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ['webhook_subscription', 'event_type', 'attempt_number', 'status', 'http_status_code', 'created_at']
    search_fields = ['event_type', 'event_id']
    list_filter = ['status', 'attempt_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WebhookDeliveryMetrics)
class WebhookDeliveryMetricsAdmin(admin.ModelAdmin):
    list_display = ['webhook_subscription', 'period_start', 'total_deliveries', 'successful_deliveries', 'failed_deliveries']
    list_filter = ['period_start']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'price', 'api_limit', 'webhook_limit', 'is_active']
    search_fields = ['name', 'tier']
    list_filter = ['tier', 'is_active']

@admin.register(BillingSubscription)
class BillingSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'renewal_date', 'created_at']
    search_fields = ['user__email']
    list_filter = ['status', 'plan__tier']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'amount', 'status', 'created_at']
    search_fields = ['user__email', 'transaction_id', 'payment_intent']
    list_filter = ['provider', 'status']
    readonly_fields = ['created_at', 'updated_at', 'provider_response']

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'plan_tier_access']
    search_fields = ['name', 'code']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    search_fields = ['user__email', 'action']
    list_filter = ['action', 'created_at']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'created_at']
