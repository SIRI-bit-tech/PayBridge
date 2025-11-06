from django.db.models import Sum, Count, Avg, Q
from datetime import datetime, timedelta
from decimal import Decimal
from api.models import Transaction, APILog, UsageMetric


class AnalyticsService:
    """Real-time analytics aggregation"""
    
    @staticmethod
    def get_transaction_analytics(user, days=30):
        """Get transaction analytics for period"""
        start_date = datetime.now() - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        total_count = transactions.count()
        completed = transactions.filter(status='completed')
        
        stats = completed.aggregate(
            total_volume=Sum('amount'),
            avg_amount=Avg('amount'),
            total_fees=Sum('fee'),
            total_net=Sum('net_amount')
        )
        
        by_provider = transactions.values('provider').annotate(
            count=Count('id'),
            volume=Sum('amount'),
            success_count=Count('id', filter=Q(status='completed'))
        )
        
        by_status = transactions.values('status').annotate(
            count=Count('id'),
            volume=Sum('amount')
        )
        
        daily_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_txns = transactions.filter(
                created_at__date=date.date()
            )
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': day_txns.count(),
                'volume': str(day_txns.aggregate(Sum('amount'))['amount__sum'] or 0),
                'success_count': day_txns.filter(status='completed').count()
            })
        
        return {
            'total_transactions': total_count,
            'total_volume': str(stats['total_volume'] or 0),
            'total_fees': str(stats['total_fees'] or 0),
            'total_net': str(stats['total_net'] or 0),
            'average_transaction': str(stats['avg_amount'] or 0),
            'success_rate': (completed.count() / total_count * 100) if total_count > 0 else 0,
            'by_provider': list(by_provider),
            'by_status': list(by_status),
            'daily_data': daily_data
        }
    
    @staticmethod
    def get_api_usage_analytics(user, days=30):
        """Get API usage analytics"""
        start_date = datetime.now() - timedelta(days=days)
        
        logs = APILog.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        total_calls = logs.count()
        stats = logs.aggregate(
            total_response_time=Sum('response_time'),
            total_request_size=Sum('request_size'),
            total_response_size=Sum('response_size'),
            avg_response_time=Avg('response_time')
        )
        
        by_endpoint = logs.values('endpoint').annotate(
            count=Count('id'),
            avg_time=Avg('response_time'),
            error_count=Count('id', filter=Q(status_code__gte=400))
        )
        
        by_status = logs.values('status_code').annotate(
            count=Count('id')
        )
        
        return {
            'total_calls': total_calls,
            'avg_response_time': float(stats['avg_response_time'] or 0),
            'total_request_mb': float((stats['total_request_size'] or 0) / 1024 / 1024),
            'total_response_mb': float((stats['total_response_size'] or 0) / 1024 / 1024),
            'by_endpoint': list(by_endpoint),
            'by_status': list(by_status)
        }
    
    @staticmethod
    def get_revenue_analytics(user, days=30):
        """Get revenue analytics"""
        start_date = datetime.now() - timedelta(days=days)
        
        transactions = Transaction.objects.filter(
            user=user,
            status='completed',
            created_at__gte=start_date
        )
        
        stats = transactions.aggregate(
            gross_revenue=Sum('amount'),
            net_revenue=Sum('net_amount'),
            total_fees=Sum('fee'),
            transaction_count=Count('id')
        )
        
        by_currency = transactions.values('currency').annotate(
            gross=Sum('amount'),
            net=Sum('net_amount'),
            fees=Sum('fee')
        )
        
        return {
            'gross_revenue': str(stats['gross_revenue'] or 0),
            'net_revenue': str(stats['net_revenue'] or 0),
            'total_fees': str(stats['total_fees'] or 0),
            'transaction_count': stats['transaction_count'] or 0,
            'avg_fee_percentage': (
                (float(stats['total_fees'] or 0) / float(stats['gross_revenue'] or 1)) * 100
            ),
            'by_currency': list(by_currency)
        }
