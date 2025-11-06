from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, APILog


class AnalyticsService:
    """Transaction and API usage analytics"""
    
    @staticmethod
    def get_transaction_analytics(user, days=30):
        """Get transaction analytics for the past N days"""
        start_date = timezone.now() - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        return {
            'total_transactions': transactions.count(),
            'total_volume': float(transactions.filter(status='completed').aggregate(
                Sum('amount'))['amount__sum'] or 0),
            'total_fees': float(transactions.filter(status='completed').aggregate(
                Sum('fee'))['fee__sum'] or 0),
            'successful_count': transactions.filter(status='completed').count(),
            'failed_count': transactions.filter(status='failed').count(),
            'pending_count': transactions.filter(status='pending').count(),
            'average_amount': float(transactions.filter(status='completed').aggregate(
                Avg('amount'))['amount__avg'] or 0),
            'by_provider': AnalyticsService._transactions_by_provider(transactions),
            'by_currency': AnalyticsService._transactions_by_currency(transactions),
            'by_status': AnalyticsService._transactions_by_status(transactions),
        }
    
    @staticmethod
    def get_api_usage_analytics(user, days=30):
        """Get API usage analytics"""
        start_date = timezone.now() - timedelta(days=days)
        
        logs = APILog.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        return {
            'total_requests': logs.count(),
            'total_errors': logs.filter(status_code__gte=400).count(),
            'average_response_time': float(logs.aggregate(Avg('response_time'))['response_time__avg'] or 0),
            'total_data_transferred': {
                'request': float(logs.aggregate(Sum('request_size'))['request_size__sum'] or 0),
                'response': float(logs.aggregate(Sum('response_size'))['response_size__sum'] or 0),
            },
            'by_endpoint': AnalyticsService._requests_by_endpoint(logs),
            'by_status_code': AnalyticsService._requests_by_status_code(logs),
            'by_method': AnalyticsService._requests_by_method(logs),
        }
    
    @staticmethod
    def get_revenue_analytics(user, days=30):
        """Get revenue analytics"""
        start_date = timezone.now() - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__gte=start_date
        )
        
        total_fees = float(transactions.aggregate(Sum('fee'))['fee__sum'] or 0)
        
        return {
            'gross_volume': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0),
            'platform_fees': total_fees,
            'top_currencies': AnalyticsService._top_currencies(transactions, limit=5),
            'daily_revenue': AnalyticsService._daily_revenue(transactions),
        }
    
    @staticmethod
    def _transactions_by_provider(transactions):
        """Group transactions by provider"""
        return {
            item['provider']: item['count']
            for item in transactions.values('provider').annotate(count=Count('id'))
        }
    
    @staticmethod
    def _transactions_by_currency(transactions):
        """Group transactions by currency"""
        data = transactions.values('currency').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        return [{
            'currency': item['currency'],
            'count': item['count'],
            'total': float(item['total'] or 0)
        } for item in data]
    
    @staticmethod
    def _transactions_by_status(transactions):
        """Group transactions by status"""
        return {
            item['status']: item['count']
            for item in transactions.values('status').annotate(count=Count('id'))
        }
    
    @staticmethod
    def _requests_by_endpoint(logs):
        """Group API requests by endpoint"""
        return {
            item['endpoint']: item['count']
            for item in logs.values('endpoint').annotate(count=Count('id')).order_by('-count')[:10]
        }
    
    @staticmethod
    def _requests_by_status_code(logs):
        """Group requests by status code"""
        return {
            str(item['status_code']): item['count']
            for item in logs.values('status_code').annotate(count=Count('id'))
        }
    
    @staticmethod
    def _requests_by_method(logs):
        """Group requests by HTTP method"""
        return {
            item['method']: item['count']
            for item in logs.values('method').annotate(count=Count('id'))
        }
    
    @staticmethod
    def _top_currencies(transactions, limit=5):
        """Get top currencies by volume"""
        data = transactions.values('currency').annotate(
            total=Sum('amount')
        ).order_by('-total')[:limit]
        return [{
            'currency': item['currency'],
            'total': float(item['total'] or 0)
        } for item in data]
    
    @staticmethod
    def _daily_revenue(transactions):
        """Get daily revenue breakdown"""
        from django.db.models.functions import TruncDate
        data = transactions.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_fees=Sum('fee'),
            transaction_count=Count('id')
        ).order_by('date')
        return [{
            'date': item['date'].isoformat(),
            'revenue': float(item['total_fees'] or 0),
            'count': item['transaction_count']
        } for item in data]
