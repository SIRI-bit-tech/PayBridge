"""
Serializers for webhook models
"""
from rest_framework import serializers
from .webhook_models import (
    WebhookEvent, WebhookSubscription, WebhookDeliveryLog, WebhookDeliveryMetrics
)


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for incoming provider webhook events"""
    
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'provider', 'provider_event_id', 'canonical_event_type',
            'raw_payload', 'signature_valid', 'received_at', 'processed_at',
            'processing_status', 'processing_error', 'created_at'
        ]
        read_only_fields = fields


class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for client webhook subscriptions"""
    masked_secret = serializers.SerializerMethodField()
    health_status = serializers.CharField(source='last_delivery_status', read_only=True)
    
    class Meta:
        model = WebhookSubscription
        fields = [
            'id', 'url', 'secret_key', 'masked_secret', 'selected_events',
            'active', 'health_status', 'last_delivery_at', 'failure_count',
            'success_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'secret_key', 'masked_secret', 'health_status', 
                           'last_delivery_at', 'failure_count', 'success_count', 
                           'created_at', 'updated_at']
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }
    
    def get_masked_secret(self, obj):
        """Return masked version of secret key"""
        if len(obj.secret_key) > 12:
            return f"{obj.secret_key[:10]}...{obj.secret_key[-4:]}"
        return "****"
    
    def to_representation(self, instance):
        """Customize representation to show full secret only on creation"""
        data = super().to_representation(instance)
        
        # Only show full secret key on creation (when it's in context)
        if self.context.get('show_secret', False):
            data['secret_key'] = instance.secret_key
        else:
            data.pop('secret_key', None)
        
        return data


class WebhookDeliveryLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook delivery logs"""
    webhook_url = serializers.CharField(source='webhook_subscription.url', read_only=True)
    
    class Meta:
        model = WebhookDeliveryLog
        fields = [
            'id', 'webhook_subscription', 'webhook_url', 'webhook_event',
            'event_id', 'event_type', 'attempt_number', 'status',
            'http_status_code', 'response_body', 'latency_ms',
            'error_message', 'next_retry_at', 'created_at'
        ]
        read_only_fields = fields


class WebhookDeliveryMetricsSerializer(serializers.ModelSerializer):
    """Serializer for webhook delivery metrics"""
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = WebhookDeliveryMetrics
        fields = [
            'id', 'webhook_subscription', 'period_start', 'period_end',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'retry_count', 'dead_letter_count', 'avg_latency_ms',
            'p95_latency_ms', 'p99_latency_ms', 'success_rate'
        ]
        read_only_fields = fields
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        return round(obj.success_rate(), 2)
