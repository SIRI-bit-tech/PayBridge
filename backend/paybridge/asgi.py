import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from api.consumers import DashboardConsumer, TransactionConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    path('ws/dashboard/', AuthMiddlewareStack(DashboardConsumer.as_asgi())),
    path('ws/transaction/<str:transaction_id>/', AuthMiddlewareStack(TransactionConsumer.as_asgi())),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
