from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from api.graphql_view import AuthenticatedGraphQLView
from api.webhook_views import (
    paystack_webhook, flutterwave_webhook, 
    stripe_webhook, chapa_webhook
)
from api.views import RegisterView

schema_view = get_schema_view(
    openapi.Info(
        title="PayBridge API",
        default_version='v1',
        description="""
        PayBridge - Pan-African Payment Aggregation Platform
        
        Complete payment processing API supporting:
        - Paystack, Flutterwave, Stripe, Mono, Okra, Chapa, Lazerpay
        - KYC verification with Mono and Okra
        - Real-time transaction analytics
        - Webhook management with HMAC signatures
        - Comprehensive billing and subscription management
        - API key management with IP whitelisting
        """,
        contact=openapi.Contact(email="support@paybridge.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # GraphQL endpoint
    path('api/v1/graphql/', AuthenticatedGraphQLView.as_view(graphiql=True), name='graphql'),
    
    # Authentication
    path('api/v1/auth/register/', RegisterView.as_view(), name='register'),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API v1 routes
    path('api/v1/', include('api.urls')),
    
    # Webhooks
    path('api/v1/webhooks/paystack/', paystack_webhook, name='paystack_webhook'),
    path('api/v1/webhooks/flutterwave/', flutterwave_webhook, name='flutterwave_webhook'),
    path('api/v1/webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    path('api/v1/webhooks/chapa/', chapa_webhook, name='chapa_webhook'),
]
