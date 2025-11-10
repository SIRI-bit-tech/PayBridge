import os
import socketio
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import Socket.IO server after Django is initialized
from api.socketio_server import sio

# Wrap Django application with Socket.IO
application = socketio.ASGIApp(
    sio,
    django_asgi_app,
    socketio_path='socket.io'
)
