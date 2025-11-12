"""
Redis Pub/Sub Listener for Billing Events
"""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from django.conf import settings
from .socketio_server import emit_plan_update, emit_usage_update, emit_limit_reached

logger = logging.getLogger(__name__)


class BillingRedisListener:
    """Listen to Redis pub/sub for billing events and broadcast via Socket.IO"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        self.running = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to billing channels
            await self.pubsub.subscribe('billing_updates', 'billing_usage')
            
            logger.info("Connected to Redis pub/sub for billing events")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def listen(self):
        """Listen for messages and broadcast to Socket.IO"""
        self.running = True
        
        try:
            async for message in self.pubsub.listen():
                if not self.running:
                    break
                
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        channel = message['channel']
                        
                        await self.handle_message(channel, data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error handling message: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Redis listener: {str(e)}")
        finally:
            await self.disconnect()
    
    async def handle_message(self, channel, data):
        """Handle incoming Redis message"""
        try:
            event_type = data.get('type')
            user_id = data.get('user_id')
            
            if not user_id:
                logger.warning(f"No user_id in message: {data}")
                return
            
            if channel == 'billing_updates':
                # Plan updates (upgrade, downgrade, renewal, cancellation)
                if event_type in ['plan:update', 'plan:assigned', 'plan:renewed', 'plan:downgraded', 'plan:cancelled']:
                    await emit_plan_update(user_id, data)
            
            elif channel == 'billing_usage':
                # Usage updates
                if event_type == 'usage:update':
                    await emit_usage_update(user_id, data)
                elif event_type == 'plan:limit_reached':
                    await emit_limit_reached(user_id, data)
            
            logger.debug(f"Handled {event_type} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        self.running = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe('billing_updates', 'billing_usage')
            await self.pubsub.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Disconnected from Redis pub/sub")
    
    async def start(self):
        """Start the listener"""
        await self.connect()
        await self.listen()


# Global listener instance
billing_listener = BillingRedisListener()


async def start_billing_listener():
    """Start the billing Redis listener"""
    try:
        await billing_listener.start()
    except Exception as e:
        logger.error(f"Failed to start billing listener: {str(e)}")


def run_billing_listener():
    """Run the billing listener in an event loop"""
    asyncio.run(start_billing_listener())
