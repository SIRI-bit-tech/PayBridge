"""
ASGI routing configuration for WebSocket connections
"""
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.consumers import DashboardConsumer, TransactionConsumer, APIKeyConsumer

websocket_urlpatterns = [
    path('ws/dashboard/', DashboardConsumer.as_asgi()),
    path('ws/transaction/<str:transaction_id>/', TransactionConsumer.as_asgi()),
    path('ws/api-keys/', APIKeyConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
