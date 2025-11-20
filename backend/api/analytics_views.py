from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, APILog
from .webhook_models import WebhookSubscription
import logging

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet):
    """System analytics and health metrics"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='system-health')
    def system_health(self, request):
        """Get system health metrics"""
        user = request.user
        today = timezone.now().date()
        
        # Webhook delivery rate (last 24 hours)
        # Use new webhook system
        active_webhooks = WebhookSubscription.objects.filter(
            user=user,
            active=True
        ).count()
        
        # Calculate delivery rate from webhook subscriptions
        total_deliveries = sum([
            ws.success_count + ws.failure_count 
            for ws in WebhookSubscription.objects.filter(user=user)
        ])
        successful_deliveries = sum([
            ws.success_count 
            for ws in WebhookSubscription.objects.filter(user=user)
        ])
        
        webhook_delivery_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 100.0
        
        # Average response time from API logs
        api_logs = APILog.objects.filter(
            user=user,
            created_at__date=today
        )
        
        avg_response = api_logs.aggregate(
            avg_time=Avg('response_time')
        )['avg_time'] or 150  # Default 150ms
        
        # Total requests today
        total_requests = api_logs.count()
        
        # Failed requests (4xx, 5xx status codes)
        failed_requests = api_logs.filter(
            Q(status_code__gte=400)
        ).count()
        
        # System uptime (based on successful transactions)
        total_txns = Transaction.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        successful_txns = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        uptime_percentage = (successful_txns / total_txns * 100) if total_txns > 0 else 99.9
        
        return Response({
            'webhook_delivery_rate': webhook_delivery_rate,
            'avg_response_time': int(avg_response),
            'uptime_percentage': uptime_percentage,
            'total_requests_today': total_requests,
            'failed_requests_today': failed_requests,
        })
    
    @action(detail=False, methods=['get'], url_path='performance')
    def performance(self, request):
        """Get performance metrics over time"""
        user = request.user
        
        # Last 7 days performance
        performance_data = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            
            day_logs = APILog.objects.filter(
                user=user,
                created_at__date=date
            )
            
            avg_response = day_logs.aggregate(
                avg_time=Avg('response_time')
            )['avg_time'] or 0
            
            total_requests = day_logs.count()
            failed_requests = day_logs.filter(
                Q(status_code__gte=400)
            ).count()
            
            performance_data.append({
                'date': date.isoformat(),
                'avg_response_time': int(avg_response),
                'total_requests': total_requests,
                'failed_requests': failed_requests,
                'success_rate': ((total_requests - failed_requests) / total_requests * 100) if total_requests > 0 else 100
            })
        
        return Response(performance_data)
