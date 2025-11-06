from django.contrib import admin
from .models import (
    UserProfile, APIKey, PaymentProvider, Transaction,
    Webhook, Subscription, AuditLog
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

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'is_active', 'last_triggered']
    search_fields = ['user__email', 'url']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'renewal_date']
    search_fields = ['user__email']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    search_fields = ['user__email', 'action']
    list_filter = ['action', 'created_at']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'created_at']
