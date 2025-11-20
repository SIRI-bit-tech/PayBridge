import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q, Sum, Count
from decimal import Decimal
from datetime import datetime, timedelta
from .models import (
    Transaction, PaymentProvider, APIKey,
    AuditLog, KYCVerification, APILog, Invoice
)
from .webhook_models import WebhookSubscription
from .billing_models import BillingSubscription


class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'provider', 'amount', 'currency', 
            'status', 'reference', 'customer_email', 'description',
            'fee', 'net_amount', 'created_at', 'updated_at'
        ]


class PaymentProviderType(DjangoObjectType):
    class Meta:
        model = PaymentProvider
        fields = ['id', 'provider', 'is_live', 'is_active', 'created_at']


class APIKeyType(DjangoObjectType):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'status', 'last_used', 'created_at']


class WebhookType(DjangoObjectType):
    class Meta:
        model = WebhookSubscription
        fields = ['id', 'url', 'event_types', 'is_active', 'last_triggered']


class SubscriptionType(DjangoObjectType):
    class Meta:
        model = BillingSubscription
        fields = ['plan', 'status', 'current_period_start', 'current_period_end']


class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'status', 'amount', 'total', 'due_date']


class AnalyticsType(graphene.ObjectType):
    """Real-time analytics data aggregation"""
    total_transactions = graphene.Int()
    total_volume = graphene.Decimal()
    success_rate = graphene.Float()
    average_transaction_size = graphene.Decimal()
    transactions_by_provider = graphene.JSONString()
    transactions_by_status = graphene.JSONString()
    daily_volume = graphene.List(graphene.JSONString)
    
    def resolve_total_transactions(self, info, **kwargs):
        user = info.context.user
        return Transaction.objects.filter(user=user).count()
    
    def resolve_total_volume(self, info, **kwargs):
        user = info.context.user
        result = Transaction.objects.filter(
            user=user, status='completed'
        ).aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0')
    
    def resolve_success_rate(self, info, **kwargs):
        user = info.context.user
        total = Transaction.objects.filter(user=user).count()
        if total == 0:
            return 0.0
        successful = Transaction.objects.filter(
            user=user, status='completed'
        ).count()
        return (successful / total) * 100
    
    def resolve_average_transaction_size(self, info, **kwargs):
        user = info.context.user
        result = Transaction.objects.filter(
            user=user, status='completed'
        ).aggregate(avg=Sum('amount') / Count('id'))
        return result['avg'] or Decimal('0')
    
    def resolve_transactions_by_provider(self, info, **kwargs):
        user = info.context.user
        providers = Transaction.objects.filter(user=user).values('provider').annotate(
            count=Count('id'),
            volume=Sum('amount')
        )
        return {p['provider']: {'count': p['count'], 'volume': str(p['volume'])} for p in providers}
    
    def resolve_transactions_by_status(self, info, **kwargs):
        user = info.context.user
        statuses = Transaction.objects.filter(user=user).values('status').annotate(
            count=Count('id')
        )
        return {s['status']: s['count'] for s in statuses}
    
    def resolve_daily_volume(self, info, **kwargs):
        user = info.context.user
        last_30_days = Transaction.objects.filter(
            user=user,
            created_at__gte=datetime.now() - timedelta(days=30)
        ).values('created_at__date').annotate(
            volume=Sum('amount'),
            count=Count('id')
        ).order_by('created_at__date')
        
        return [
            {
                'date': str(d['created_at__date']),
                'volume': str(d['volume']),
                'count': d['count']
            }
            for d in last_30_days
        ]


class Query(graphene.ObjectType):
    """GraphQL Query root for multi-provider unified access"""
    
    # Transactions
    transactions = graphene.List(
        TransactionType,
        status=graphene.String(),
        provider=graphene.String(),
        currency=graphene.String()
    )
    transaction = graphene.Field(TransactionType, reference=graphene.String())
    
    # Payment Providers
    payment_providers = graphene.List(PaymentProviderType)
    payment_provider = graphene.Field(PaymentProviderType, provider=graphene.String())
    
    # API Keys
    api_keys = graphene.List(APIKeyType)
    api_key = graphene.Field(APIKeyType, id=graphene.String())
    
    # Webhooks
    webhooks = graphene.List(WebhookType)
    webhook = graphene.Field(WebhookType, id=graphene.String())
    
    # Subscription
    subscription = graphene.Field(SubscriptionType)
    
    # Analytics
    analytics = graphene.Field(AnalyticsType)
    
    # Invoices
    invoices = graphene.List(InvoiceType)
    invoice = graphene.Field(InvoiceType, id=graphene.String())
    
    def resolve_transactions(self, info, status=None, provider=None, currency=None, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return Transaction.objects.none()
        
        queryset = Transaction.objects.filter(user=user)
        
        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)
        if provider:
            queryset = queryset.filter(provider=provider)
        if currency:
            queryset = queryset.filter(currency=currency)
        
        return queryset.order_by('-created_at')[:20]  # Limit to 20 results
    
    def resolve_transaction(self, info, reference):
        user = info.context.user
        try:
            return Transaction.objects.get(user=user, reference=reference)
        except Transaction.DoesNotExist:
            return None
    
    def resolve_payment_providers(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return []
        return PaymentProvider.objects.filter(user=user)
    
    def resolve_payment_provider(self, info, provider):
        user = info.context.user
        try:
            return PaymentProvider.objects.get(user=user, provider=provider)
        except PaymentProvider.DoesNotExist:
            return None
    
    def resolve_api_keys(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return []
        return APIKey.objects.filter(user=user)
    
    def resolve_api_key(self, info, id):
        user = info.context.user
        try:
            return APIKey.objects.get(user=user, id=id)
        except APIKey.DoesNotExist:
            return None
    
    def resolve_webhooks(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return []
        return WebhookSubscription.objects.filter(user=user)
    
    def resolve_webhook(self, info, id):
        user = info.context.user
        try:
            return WebhookSubscription.objects.get(user=user, id=id)
        except WebhookSubscription.DoesNotExist:
            return None
    
    def resolve_subscription(self, info):
        user = info.context.user
        try:
            return BillingSubscription.objects.get(user=user)
        except BillingSubscription.DoesNotExist:
            return None
    
    def resolve_analytics(self, info):
        return AnalyticsType()
    
    def resolve_invoices(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return []
        return Invoice.objects.filter(user=user)
    
    def resolve_invoice(self, info, id):
        user = info.context.user
        try:
            return Invoice.objects.get(user=user, id=id)
        except Invoice.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
