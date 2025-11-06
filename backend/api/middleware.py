import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from .models import AuditLog, APILog
import json

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Centralized error handling middleware"""
    def process_exception(self, request, exception):
        logger.error(f"Exception: {str(exception)}", exc_info=True)
        if request.user and request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action='error',
                ip_address=self.get_client_ip(request),
                details={'error': str(exception)}
            )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor API performance and log metrics"""
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            elapsed = (time.time() - request._start_time) * 1000  # Convert to ms
            
            # Log slow requests
            if elapsed > 1000:  # > 1 second
                logger.warning(f"Slow request: {request.path} took {elapsed:.2f}ms")
            
            # Log API metrics for authenticated users
            if request.user and request.user.is_authenticated and '/api/' in request.path:
                try:
                    response_size = len(response.content) if hasattr(response, 'content') else 0
                    
                    APILog.objects.create(
                        user=request.user,
                        endpoint=request.path,
                        method=request.method,
                        status_code=response.status_code,
                        response_time=elapsed,
                        response_size=response_size,
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    )
                except Exception as e:
                    logger.error(f"Error logging API metrics: {str(e)}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class RateLimitMiddleware(MiddlewareMixin):
    """Advanced rate limiting middleware for scalability"""
    
    RATE_LIMITS = {
        '/api/v1/transactions/initiate_payment/': {'requests': 100, 'window': 3600},
        '/api/v1/kyc/': {'requests': 50, 'window': 3600},
        '/api/v1/webhooks/': {'requests': 1000, 'window': 3600},
        '/api/v1/transactions/': {'requests': 500, 'window': 3600},
        '/api/v1/api-keys/': {'requests': 50, 'window': 3600},
    }
    
    def process_request(self, request):
        if not request.user or not request.user.is_authenticated:
            return None
        
        # Check rate limits
        user_id = request.user.id
        client_ip = self.get_client_ip(request)
        endpoint = request.path
        
        # Find matching rate limit config
        limit_config = None
        for path_pattern, config in self.RATE_LIMITS.items():
            if endpoint.startswith(path_pattern):
                limit_config = config
                break
        
        if not limit_config:
            return None
        
        # Create cache key
        cache_key = f"rate_limit:{user_id}:{client_ip}:{endpoint}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit_config['requests']:
            logger.warning(f"Rate limit exceeded for user {user_id} on {endpoint}")
            return self.get_rate_limit_response()
        
        # Increment counter
        cache.set(cache_key, current_count + 1, limit_config['window'])
        
        return None
    
    def get_rate_limit_response(self):
        from django.http import JsonResponse
        return JsonResponse(
            {'error': 'Rate limit exceeded. Please try again later.'},
            status=429
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class ConnectionPoolMiddleware(MiddlewareMixin):
    """Middleware to optimize database connection pooling"""
    
    def process_request(self, request):
        # Connection pooling is configured in settings
        # This middleware ensures proper cleanup
        return None
    
    def process_response(self, request, response):
        # Ensure connections are returned to pool
        from django.db import connections
        for conn in connections.all():
            conn.close()
        return response
