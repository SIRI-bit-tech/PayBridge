"""
Billing Middleware for Plan Limit Enforcement
"""
import logging
from django.http import JsonResponse
from .usage_tracking_service import UsageTrackingService

logger = logging.getLogger(__name__)


class PlanLimitMiddleware:
    """Middleware to enforce plan limits on API requests"""
    
    # Endpoints that should be excluded from limit checks
    EXCLUDED_PATHS = [
        '/api/auth/',
        '/api/billing/',
        '/api/webhooks/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if path should be excluded
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)
        
        # Only check for authenticated users
        if request.user.is_authenticated:
            # Check if user has reached API limit
            if UsageTrackingService.check_api_limit(request.user):
                return JsonResponse({
                    'error': 'API limit reached',
                    'message': 'You have reached your monthly API call limit. Please upgrade your plan.',
                    'upgrade_url': '/billing'
                }, status=429)
            
            # Increment API call counter
            UsageTrackingService.increment_api_call(request.user)
        
        response = self.get_response(request)
        return response


class FeatureAccessMiddleware:
    """Middleware to check feature access based on plan"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check feature access for specific endpoints
        if request.user.is_authenticated:
            # Analytics endpoints
            if request.path.startswith('/api/analytics/'):
                subscription = request.user.billing_subscription
                if not subscription.plan.has_analytics:
                    return JsonResponse({
                        'error': 'Feature not available',
                        'message': 'Analytics is not available in your current plan. Please upgrade.',
                        'upgrade_url': '/billing'
                    }, status=403)
        
        response = self.get_response(request)
        return response
