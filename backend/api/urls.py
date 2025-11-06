from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, APIKeyViewSet, PaymentProviderViewSet,
    TransactionViewSet, WebhookViewSet, SubscriptionViewSet,
    KYCViewSet, AnalyticsViewSet, BillingViewSet, AuditLogViewSet
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'payment-providers', PaymentProviderViewSet, basename='payment-provider')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'kyc', KYCViewSet, basename='kyc')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'billing', BillingViewSet, basename='billing')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
