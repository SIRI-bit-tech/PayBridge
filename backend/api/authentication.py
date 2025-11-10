from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from .models import APIKey
from django.utils import timezone
import hashlib


class APIKeyAuthentication(TokenAuthentication):
    """
    Custom authentication for API key validation using SHA256 hashing
    """
    keyword = 'Bearer'
    
    def get_model(self):
        return APIKey
    
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if not auth or auth[0].lower() != self.keyword.lower():
            return None
        
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed('Invalid API key header')
        
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid API key header')
        
        try:
            token = auth[1]
        except IndexError:
            raise exceptions.AuthenticationFailed('Invalid API key')
        
        return self.authenticate_credentials(token, request)
    
    def authenticate_credentials(self, key, request):
        # Hash the provided key
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        try:
            api_key_obj = APIKey.objects.select_related('user').get(
                key_hash=key_hash, 
                status='active'
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or expired API key')
        
        # Check IP whitelist if configured
        if api_key_obj.ip_whitelist:
            client_ip = self.get_client_ip(request)
            if client_ip not in api_key_obj.ip_whitelist:
                raise exceptions.AuthenticationFailed('IP not whitelisted')
        
        # Update last_used timestamp asynchronously to avoid blocking
        from .tasks import update_api_key_last_used
        update_api_key_last_used.delay(str(api_key_obj.id))
        
        return (api_key_obj.user, api_key_obj)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
