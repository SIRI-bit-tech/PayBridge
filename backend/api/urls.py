from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserProfileViewSet, APIKeyViewSet, PaymentProviderViewSet,
    TransactionViewSet, WebhookViewSet, SubscriptionViewSet,
    KYCViewSet, AnalyticsViewSet, BillingViewSet, AuditLogViewSet,
    LoginView, RegisterView, PasswordResetRequestView, PasswordResetConfirmView
)
from .settlement_views import SettlementViewSet
from .analytics_views import AnalyticsViewSet as SystemAnalyticsViewSet

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
router.register(r'settlements', SettlementViewSet, basename='settlement')
router.register(r'system-analytics', SystemAnalyticsViewSet, basename='system-analytics')

# Authentication URLs
auth_patterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(auth_patterns)),
]
