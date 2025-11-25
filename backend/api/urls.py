from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserProfileViewSet, APIKeyViewSet, PaymentProviderViewSet,
    TransactionViewSet,
    KYCViewSet, AnalyticsViewSet, BillingViewSet, AuditLogViewSet,
    LoginView, RegisterView, PasswordResetRequestView, PasswordResetConfirmView,
    HealthCheckView
)
from .settlement_views import SettlementViewSet
from .analytics_views import AnalyticsViewSet as SystemAnalyticsViewSet
from .billing_views import (
    get_billing_plan, create_subscription, cancel_subscription,
    get_usage, get_payment_history
)
from .webhook_management_views import (
    WebhookSubscriptionViewSet, WebhookEventViewSet, WebhookDeliveryLogViewSet
)
from .webhook_receiver import (
    webhook_paystack, webhook_flutterwave, webhook_stripe, webhook_mono
)
from .settings_views import (
    BusinessProfileViewSet, PaymentProviderConfigViewSet
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'payment-providers', PaymentProviderViewSet, basename='payment-provider')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'webhook-subscriptions', WebhookSubscriptionViewSet, basename='webhook-subscription')
router.register(r'webhook-events', WebhookEventViewSet, basename='webhook-event')
router.register(r'webhook-deliveries', WebhookDeliveryLogViewSet, basename='webhook-delivery')
router.register(r'settings/business-profile', BusinessProfileViewSet, basename='business-profile')
router.register(r'settings/providers', PaymentProviderConfigViewSet, basename='provider-config')
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

# Billing URLs
billing_patterns = [
    path('billing/plan/', get_billing_plan, name='billing_plan'),
    path('billing/subscribe/', create_subscription, name='create_subscription'),
    path('billing/cancel/', cancel_subscription, name='cancel_subscription'),
    path('billing/usage/', get_usage, name='get_usage'),
    path('billing/payments/', get_payment_history, name='payment_history'),
]

# Provider Webhook Receiver URLs (public endpoints)
webhook_patterns = [
    path('webhooks/paystack/', webhook_paystack, name='webhook_paystack'),
    path('webhooks/flutterwave/', webhook_flutterwave, name='webhook_flutterwave'),
    path('webhooks/stripe/', webhook_stripe, name='webhook_stripe'),
    path('webhooks/mono/', webhook_mono, name='webhook_mono'),
]

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)),
    path('', include(auth_patterns)),
    path('', include(billing_patterns)),
    path('', include(webhook_patterns)),
]
