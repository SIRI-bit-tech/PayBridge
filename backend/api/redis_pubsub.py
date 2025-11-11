"""
Redis Pub/Sub service for transaction events
Enables multi-server Socket.IO synchronization
"""
import redis
import json
import logging
import os
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Redis channels
TRANSACTION_EVENTS_CHANNEL = 'paybridge:transaction_events'
API_KEY_EVENTS_CHANNEL = 'paybridge:api_key_events'


class RedisPublisher:
    """Redis publisher for broadcasting events across server instances"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis publisher connected to {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
    
    def publish_transaction_event(self, event_type: str, user_id: int, data: Dict[str, Any]):
        """
        Publish transaction event to Redis
        
        Args:
            event_type: 'new' or 'update'
            user_id: User ID who owns the transaction
            data: Transaction data dictionary
        """
        if not self.redis_client:
            logger.warning("Redis not available, skipping event publish")
            return
        
        try:
            message = {
                'event_type': event_type,
                'user_id': user_id,
                'data': data,
            }
            
            self.redis_client.publish(
                TRANSACTION_EVENTS_CHANNEL,
                json.dumps(message)
            )
            
            logger.info(f"Published transaction:{event_type} event for user {user_id} to Redis")
        except Exception as e:
            logger.error(f"Failed to publish transaction event: {str(e)}")
    
    def publish_api_key_event(self, event_type: str, user_id: int, data: Dict[str, Any]):
        """
        Publish API key event to Redis
        
        Args:
            event_type: 'created', 'revoked', or 'used'
            user_id: User ID who owns the API key
            data: API key data dictionary
        """
        if not self.redis_client:
            logger.warning("Redis not available, skipping event publish")
            return
        
        try:
            message = {
                'event_type': event_type,
                'user_id': user_id,
                'data': data,
            }
            
            self.redis_client.publish(
                API_KEY_EVENTS_CHANNEL,
                json.dumps(message)
            )
            
            logger.info(f"Published api_key:{event_type} event for user {user_id} to Redis")
        except Exception as e:
            logger.error(f"Failed to publish API key event: {str(e)}")


class RedisSubscriber:
    """Redis subscriber for receiving events from other server instances"""
    
    def __init__(self, socketio_server):
        self.sio = socketio_server
        self.redis_client = None
        self.pubsub = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis and subscribe to channels"""
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            
            # Test connection
            self.redis_client.ping()
            
            # Create pubsub instance
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to channels
            self.pubsub.subscribe(TRANSACTION_EVENTS_CHANNEL)
            self.pubsub.subscribe(API_KEY_EVENTS_CHANNEL)
            
            logger.info(f"Redis subscriber connected and subscribed to channels")
        except Exception as e:
            logger.error(f"Failed to connect Redis subscriber: {str(e)}")
            self.redis_client = None
            self.pubsub = None
    
    async def listen(self):
        """Listen for Redis pub/sub messages and emit to Socket.IO"""
        if not self.pubsub:
            logger.warning("Redis pubsub not available, skipping listener")
            return
        
        logger.info("Starting Redis pub/sub listener...")
        
        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    await self._handle_message(message)
        except Exception as e:
            logger.error(f"Error in Redis listener: {str(e)}")
            # Attempt to reconnect
            await asyncio.sleep(5)
            self._connect()
            await self.listen()
    
    async def _handle_message(self, message):
        """Handle incoming Redis message"""
        try:
            channel = message['channel']
            data = json.loads(message['data'])
            
            if channel == TRANSACTION_EVENTS_CHANNEL:
                await self._handle_transaction_event(data)
            elif channel == API_KEY_EVENTS_CHANNEL:
                await self._handle_api_key_event(data)
        except Exception as e:
            logger.error(f"Error handling Redis message: {str(e)}")
    
    async def _handle_transaction_event(self, data):
        """Handle transaction event from Redis"""
        event_type = data.get('event_type')
        user_id = data.get('user_id')
        transaction_data = data.get('data')
        
        if not all([event_type, user_id, transaction_data]):
            logger.warning("Invalid transaction event data")
            return
        
        room = f"transactions_{user_id}"
        
        if event_type == 'new':
            await self.sio.emit('transaction:new', transaction_data, room=room)
            logger.info(f"Emitted transaction:new to room {room} from Redis")
        elif event_type == 'update':
            await self.sio.emit('transaction:update', transaction_data, room=room)
            logger.info(f"Emitted transaction:update to room {room} from Redis")
    
    async def _handle_api_key_event(self, data):
        """Handle API key event from Redis"""
        event_type = data.get('event_type')
        user_id = data.get('user_id')
        api_key_data = data.get('data')
        
        if not all([event_type, user_id, api_key_data]):
            logger.warning("Invalid API key event data")
            return
        
        room = f"api_keys_{user_id}"
        
        if event_type == 'created':
            await self.sio.emit('api_key_created', api_key_data, room=room)
            logger.info(f"Emitted api_key_created to room {room} from Redis")
        elif event_type == 'revoked':
            await self.sio.emit('api_key_revoked', api_key_data, room=room)
            logger.info(f"Emitted api_key_revoked to room {room} from Redis")
        elif event_type == 'used':
            await self.sio.emit('api_key_used', api_key_data, room=room)
            logger.info(f"Emitted api_key_used to room {room} from Redis")


# Global publisher instance
redis_publisher = RedisPublisher()


def publish_transaction_new(user_id: int, transaction_data: Dict[str, Any]):
    """Publish new transaction event"""
    redis_publisher.publish_transaction_event('new', user_id, transaction_data)


def publish_transaction_update(user_id: int, transaction_data: Dict[str, Any]):
    """Publish transaction update event"""
    redis_publisher.publish_transaction_event('update', user_id, transaction_data)


def publish_api_key_created(user_id: int, api_key_data: Dict[str, Any]):
    """Publish API key created event"""
    redis_publisher.publish_api_key_event('created', user_id, api_key_data)


def publish_api_key_revoked(user_id: int, api_key_data: Dict[str, Any]):
    """Publish API key revoked event"""
    redis_publisher.publish_api_key_event('revoked', user_id, api_key_data)


def publish_api_key_used(user_id: int, api_key_data: Dict[str, Any]):
    """Publish API key used event"""
    redis_publisher.publish_api_key_event('used', user_id, api_key_data)
