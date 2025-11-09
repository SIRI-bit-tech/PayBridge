from graphene_django.views import GraphQLView
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


@method_decorator(csrf_exempt, name='dispatch')
class AuthenticatedGraphQLView(GraphQLView):
    """GraphQL view with JWT authentication support (CSRF exempt)"""
    
    def dispatch(self, request, *args, **kwargs):
        # Try to authenticate using JWT
        jwt_auth = JWTAuthentication()
        
        try:
            # Get the authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if auth_header.startswith('Bearer '):
                # Authenticate the request
                auth_result = jwt_auth.authenticate(request)
                
                if auth_result is not None:
                    user, token = auth_result
                    request.user = user
                else:
                    request.user = AnonymousUser()
            else:
                request.user = AnonymousUser()
                
        except (AuthenticationFailed, Exception) as e:
            # If authentication fails, set anonymous user
            request.user = AnonymousUser()
        
        return super().dispatch(request, *args, **kwargs)
