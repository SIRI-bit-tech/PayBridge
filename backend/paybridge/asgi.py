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
from api.billing_redis_listener import billing_listener

logger = logging.getLogger(__name__)

# Create Redis subscriber for multi-server synchronization
redis_subscriber = RedisSubscriber(sio)

# Start Redis listeners in background
async def start_redis_listener():
    """Start Redis pub/sub listener in background"""
    try:
        logger.info("Connecting to Redis and starting listener...")
        await redis_subscriber._connect()
        await redis_subscriber.listen()
    except Exception as e:
        logger.exception(f"Redis listener error: {str(e)}")

async def start_billing_listener():
    """Start billing Redis pub/sub listener in background"""
    try:
        logger.info("Starting billing Redis listener...")
        await billing_listener.start()
    except Exception as e:
        logger.exception(f"Billing listener error: {str(e)}")

# Schedule Redis listeners to start
try:
    loop = asyncio.get_event_loop()
    loop.create_task(start_redis_listener())
    loop.create_task(start_billing_listener())
    logger.info("Redis listener tasks scheduled")
except Exception as e:
    logger.warning(f"Could not start Redis listeners: {str(e)}")

# Wrap Django application with Socket.IO
application = socketio.ASGIApp(
    sio,
    django_asgi_app,
    socketio_path='socket.io'
)
