import os
import socketio
import asyncio
import logging
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paybridge.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import Socket.IO server after Django is initialized
from api.socketio_server import sio
from api.redis_pubsub import RedisSubscriber

logger = logging.getLogger(__name__)

# Create Redis subscriber for multi-server synchronization
redis_subscriber = RedisSubscriber(sio)

# Start Redis listener in background
async def start_redis_listener():
    """Start Redis pub/sub listener in background"""
    try:
        logger.info("Starting Redis pub/sub listener...")
        await redis_subscriber.listen()
    except Exception as e:
        logger.error(f"Redis listener error: {str(e)}")

# Schedule Redis listener to start
try:
    loop = asyncio.get_event_loop()
    loop.create_task(start_redis_listener())
    logger.info("Redis listener task scheduled")
except Exception as e:
    logger.warning(f"Could not start Redis listener: {str(e)}")

# Wrap Django application with Socket.IO
application = socketio.ASGIApp(
    sio,
    django_asgi_app,
    socketio_path='socket.io'
)
