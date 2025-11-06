from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, APIKey, PaymentProvider, Transaction, 
    Webhook, Subscription, AuditLog, KYCVerification,
    Invoice, UsageMetric, WebhookEvent
)


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['email', 'company_name', 'country', 'phone_number', 'business_type', 'kyc_verified']


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'status', 'last_used', 'created_at']
        read_only_fields = ['id', 'key', 'secret', 'last_used', 'created_at']


class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = ['id', 'provider', 'is_live', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'amount', 'currency', 'status', 
            'provider', 'customer_email', 'description', 'fee', 
            'net_amount', 'created_at'
        ]
        read_only_fields = ['id', 'reference', 'fee', 'net_amount', 'created_at']


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['id', 'url', 'event_types', 'is_active', 'last_triggered', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['plan', 'status', 'current_period_start', 'current_period_end', 'renewal_date']
        read_only_fields = ['status', 'current_period_start', 'current_period_end', 'renewal_date']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['action', 'ip_address', 'user_agent', 'details', 'created_at']
        read_only_fields = ['action', 'ip_address', 'user_agent', 'details', 'created_at']

class KYCVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCVerification
        fields = ['id', 'verification_type', 'verification_id', 'status', 'provider', 'verified_at', 'created_at']
        read_only_fields = ['id', 'status', 'verified_at', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'status', 'amount', 'tax', 'total', 'due_date', 'paid_date', 'created_at']
        read_only_fields = ['id', 'invoice_number', 'created_at']


class UsageMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageMetric
        fields = ['id', 'period_start', 'period_end', 'api_calls', 'transaction_volume', 'data_transferred_mb', 'cost']
        read_only_fields = ['id', 'api_calls', 'transaction_volume', 'data_transferred_mb', 'cost']


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_type', 'status', 'response_status_code', 'attempt', 'created_at']
        read_only_fields = ['id', 'created_at']
