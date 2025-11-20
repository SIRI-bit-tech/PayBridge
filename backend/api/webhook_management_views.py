"""
Webhook Management API Views
Allows developers to register, manage, and monitor their webhook endpoints
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .webhook_models import (
    WebhookSubscription, WebhookDeliveryLog, WebhookDeliveryMetrics, WebhookEvent
)
from .webhook_serializers import (
    WebhookSubscriptionSerializer, WebhookDeliveryLogSerializer,
    WebhookDeliveryMetricsSerializer, WebhookEventSerializer
)
from .webhook_tasks import deliver_client_webhook
from .models import AuditLog

logger = logging.getLogger(__name__)


class WebhookSubscriptionViewSet(viewsets.ModelViewSet):
    """
    Manage webhook subscriptions (client endpoints)
    """
    serializer_class = WebhookSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WebhookSubscription.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Register a new webhook endpoint"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save(user=request.user)
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='create_webhook',
            ip_address=self.get_client_ip(request),
            details={
                'webhook_id': str(subscription.id),
                'url': subscription.url,
                'events': subscription.selected_events
            }
        )
        
        serializer = self.get_serializer(subscription, context={'show_secret': True})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update webhook subscription"""
        subscription = self.get_object()
        
        url = request.data.get('url', subscription.url)
        selected_events = request.data.get('selected_events', subscription.selected_events)
        active = request.data.get('active', subscription.active)
        
        subscription.url = url
        subscription.selected_events = selected_events
        subscription.active = active
        subscription.save()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='update_webhook',
            ip_address=self.get_client_ip(request),
            details={
                'webhook_id': str(subscription.id),
                'url': url,
                'active': active
            }
        )
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete webhook subscription"""
        subscription = self.get_object()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='delete_webhook',
            ip_address=self.get_client_ip(request),
            details={
                'webhook_id': str(subscription.id),
                'url': subscription.url
            }
        )
        
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test webhook to the endpoint"""
        subscription = self.get_object()
        
        # Create a test webhook event
        test_event = WebhookEvent.objects.create(
            provider='stripe',
            provider_event_id=f"test_{timezone.now().timestamp()}",
            canonical_event_type='test.webhook',
            raw_payload={
                'test': True,
                'message': 'This is a test webhook from PayBridge',
                'timestamp': timezone.now().isoformat()
            },
            signature_valid=True,
            processing_status='succeeded',
            processed_at=timezone.now()
        )
        
        # Trigger delivery
        deliver_client_webhook.delay(
            str(subscription.id),
            str(test_event.id),
            'test.webhook',
            attempt_number=1
        )
        
        return Response({
            'message': 'Test webhook queued for delivery',
            'event_id': str(test_event.id)
        })
    
    @action(detail=True, methods=['post'])
    def rotate_secret(self, request, pk=None):
        """Rotate the webhook secret key"""
        subscription = self.get_object()
        
        old_secret = subscription.secret_key[:10] + '...'
        new_secret = subscription.rotate_secret()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='rotate_webhook_secret',
            ip_address=self.get_client_ip(request),
            details={
                'webhook_id': str(subscription.id),
                'old_secret_prefix': old_secret
            }
        )
        
        return Response({
            'message': 'Secret key rotated successfully',
            'new_secret': new_secret
        })
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle webhook active status"""
        subscription = self.get_object()
        subscription.active = not subscription.active
        subscription.save()
        
        return Response({
            'message': f"Webhook {'activated' if subscription.active else 'deactivated'}",
            'active': subscription.active
        })
    
    @action(detail=True, methods=['get'])
    def delivery_logs(self, request, pk=None):
        """Get delivery logs for this webhook"""
        subscription = self.get_object()
        
        logs = WebhookDeliveryLog.objects.filter(
            webhook_subscription=subscription
        ).order_by('-created_at')[:100]
        
        serializer = WebhookDeliveryLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get delivery metrics for this webhook"""
        subscription = self.get_object()
        
        # Get metrics for last 24 hours
        metrics = WebhookDeliveryMetrics.objects.filter(
            webhook_subscription=subscription,
            period_start__gte=timezone.now() - timedelta(days=1)
        ).order_by('-period_start')
        
        serializer = WebhookDeliveryMetricsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_events(self, request):
        """List all available event types"""
        events = [
            {
                'type': 'payment.completed',
                'description': 'Payment successfully completed'
            },
            {
                'type': 'payment.failed',
                'description': 'Payment failed'
            },
            {
                'type': 'payment.refunded',
                'description': 'Payment refunded'
            },
            {
                'type': 'subscription.created',
                'description': 'Subscription created'
            },
            {
                'type': 'subscription.updated',
                'description': 'Subscription updated'
            },
            {
                'type': 'subscription.cancelled',
                'description': 'Subscription cancelled'
            },
            {
                'type': 'kyc.verified',
                'description': 'KYC verification completed'
            },
            {
                'type': 'kyc.failed',
                'description': 'KYC verification failed'
            },
            {
                'type': 'transfer.completed',
                'description': 'Transfer/payout completed'
            },
            {
                'type': 'transfer.failed',
                'description': 'Transfer/payout failed'
            },
        ]
        
        return Response({'events': events})
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get webhook dashboard statistics"""
        user = request.user
        
        # Total subscriptions
        total_subscriptions = WebhookSubscription.objects.filter(user=user).count()
        active_subscriptions = WebhookSubscription.objects.filter(user=user, active=True).count()
        
        # Delivery stats (last 24 hours)
        last_24h = timezone.now() - timedelta(hours=24)
        
        deliveries = WebhookDeliveryLog.objects.filter(
            webhook_subscription__user=user,
            created_at__gte=last_24h
        )
        
        total_deliveries = deliveries.count()
        successful_deliveries = deliveries.filter(status='success').count()
        failed_deliveries = deliveries.filter(status='failed').count()
        dead_letter_deliveries = deliveries.filter(status='dead_letter').count()
        
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Average latency
        avg_latency = deliveries.filter(
            latency_ms__isnull=False
        ).aggregate(avg=Avg('latency_ms'))['avg'] or 0
        
        # Top failing endpoints
        failing_endpoints = WebhookSubscription.objects.filter(
            user=user,
            last_delivery_status__in=['degraded', 'failing']
        ).values('url', 'last_delivery_status', 'failure_count')[:5]
        
        return Response({
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'total_deliveries_24h': total_deliveries,
            'successful_deliveries_24h': successful_deliveries,
            'failed_deliveries_24h': failed_deliveries,
            'dead_letter_deliveries_24h': dead_letter_deliveries,
            'success_rate': round(success_rate, 2),
            'avg_latency_ms': round(avg_latency, 2),
            'failing_endpoints': list(failing_endpoints)
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View incoming webhook events (for debugging and replay)
    """
    serializer_class = WebhookEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show events that resulted in deliveries to this user's webhooks
        return WebhookEvent.objects.filter(
            deliveries__webhook_subscription__user=self.request.user
        ).distinct().order_by('-received_at')
    
    @action(detail=True, methods=['post'])
    def replay(self, request, pk=None):
        """Replay a webhook event to all subscribed endpoints"""
        webhook_event = self.get_object()
        
        # Find user's subscriptions for this event type
        subscriptions = WebhookSubscription.objects.filter(
            user=request.user,
            active=True,
            selected_events__contains=[webhook_event.canonical_event_type]
        )
        
        if not subscriptions.exists():
            return Response(
                {'error': 'No active subscriptions for this event type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger deliveries
        for subscription in subscriptions:
            deliver_client_webhook.delay(
                str(subscription.id),
                str(webhook_event.id),
                webhook_event.canonical_event_type,
                attempt_number=1
            )
        
        return Response({
            'message': f'Webhook replayed to {subscriptions.count()} endpoints',
            'subscription_count': subscriptions.count()
        })


class WebhookDeliveryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View webhook delivery logs
    """
    serializer_class = WebhookDeliveryLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WebhookDeliveryLog.objects.filter(
            webhook_subscription__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Manually retry a failed delivery"""
        delivery_log = self.get_object()
        
        if delivery_log.status not in ('failed', 'dead_letter'):
            return Response(
                {'error': 'Can only retry failed or dead_letter deliveries'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if delivery_log.webhook_event is None:
            return Response(
                {'error': 'Cannot retry delivery without associated webhook event'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger immediate retry
        deliver_client_webhook.delay(
            str(delivery_log.webhook_subscription.id),
            str(delivery_log.webhook_event.id),
            delivery_log.event_type,
            attempt_number=delivery_log.attempt_number + 1
        )
        
        return Response({
            'message': 'Delivery retry queued',
            'attempt_number': delivery_log.attempt_number + 1
        })
    
    @action(detail=False, methods=['get'])
    def dead_letter_queue(self, request):
        """Get all permanently failed deliveries"""
        dead_letters = WebhookDeliveryLog.objects.filter(
            webhook_subscription__user=request.user,
            status='dead_letter'
        ).order_by('-created_at')[:50]
        
        serializer = self.get_serializer(dead_letters, many=True)
        return Response(serializer.data)
