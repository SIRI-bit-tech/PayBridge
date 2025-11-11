"""
Socket.IO server for real-time updates with Redis adapter
"""
import socketio
import logging
import os
from urllib.parse import quote_plus
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Create Redis manager for Socket.IO with URL-encoded password
if REDIS_PASSWORD:
    # URL-encode password to handle special characters
    encoded_password = quote_plus(REDIS_PASSWORD)
    redis_url = f"redis://:{encoded_password}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

try:
    # Create Socket.IO server with Redis adapter for multi-server support
    mgr = socketio.AsyncRedisManager(redis_url)
    
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins=settings.CORS_ALLOWED_ORIGINS,
        logger=True,
        engineio_logger=True,
        client_manager=mgr,
    )
    
    logger.info(f"Socket.IO server initialized with Redis adapter at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.warning(f"Failed to initialize Redis adapter: {str(e)}. Falling back to in-memory mode.")
    
    # Fallback to in-memory mode if Redis is not available
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins=settings.CORS_ALLOWED_ORIGINS,
        logger=True,
        engineio_logger=True,
    )


@database_sync_to_async
def get_user_from_token(token):
    """Validate JWT token and get user"""
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        return None


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client attempting to connect: {sid}")
    
    # Get token from auth data
    token = auth.get('token') if auth else None
    
    if not token:
        logger.warning(f"Connection rejected for {sid}: No token provided")
        return False
    
    # Validate token and get user
    user = await get_user_from_token(token)
    
    if not user:
        logger.warning(f"Connection rejected for {sid}: Invalid token")
        return False
    
    # Store user info in session
    async with sio.session(sid) as session:
        session['user_id'] = user.id
        session['user_email'] = user.email
    
    logger.info(f"Client connected: {sid} (User: {user.email})")
    
    # Send connection confirmation
    await sio.emit('connected', {'message': 'Connected successfully'}, room=sid)
    
    return True


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        async with sio.session(sid) as session:
            user_email = session.get('user_email', 'Unknown')
        logger.info(f"Client disconnected: {sid} (User: {user_email})")
    except Exception as e:
        logger.info(f"Client disconnected: {sid}")


@sio.event
async def join_api_keys(sid):
    """Join API keys room for real-time updates"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            logger.warning(f"join_api_keys failed for {sid}: No user_id in session")
            return
        
        room = f"api_keys_{user_id}"
        sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")
        
        await sio.emit('joined_api_keys', {'room': room}, room=sid)
    except Exception as e:
        logger.error(f"Error in join_api_keys: {str(e)}")


@sio.event
async def leave_api_keys(sid):
    """Leave API keys room"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            return
        
        room = f"api_keys_{user_id}"
        sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")
    except Exception as e:
        logger.error(f"Error in leave_api_keys: {str(e)}")


@sio.event
async def join_dashboard(sid):
    """Join dashboard room for real-time updates"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            logger.warning(f"join_dashboard failed for {sid}: No user_id in session")
            return
        
        room = f"dashboard_{user_id}"
        sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")
        
        await sio.emit('joined_dashboard', {'room': room}, room=sid)
    except Exception as e:
        logger.error(f"Error in join_dashboard: {str(e)}")


@sio.event
async def leave_dashboard(sid):
    """Leave dashboard room"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            return
        
        room = f"dashboard_{user_id}"
        sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")
    except Exception as e:
        logger.error(f"Error in leave_dashboard: {str(e)}")


@sio.event
async def join_transactions(sid):
    """Join transactions room for real-time updates"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            logger.warning(f"join_transactions failed for {sid}: No user_id in session")
            return
        
        room = f"transactions_{user_id}"
        sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room: {room}")
        
        await sio.emit('joined_transactions', {'room': room}, room=sid)
    except Exception as e:
        logger.error(f"Error in join_transactions: {str(e)}")


@sio.event
async def leave_transactions(sid):
    """Leave transactions room"""
    try:
        async with sio.session(sid) as session:
            user_id = session.get('user_id')
            
        if not user_id:
            return
        
        room = f"transactions_{user_id}"
        sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room: {room}")
    except Exception as e:
        logger.error(f"Error in leave_transactions: {str(e)}")


@sio.event
async def ping(sid):
    """Handle ping from client"""
    await sio.emit('pong', room=sid)


# Helper functions to emit events to specific users
async def emit_api_key_created(user_id, data):
    """Emit API key created event to user"""
    room = f"api_keys_{user_id}"
    await sio.emit('api_key_created', data, room=room)
    logger.info(f"Emitted api_key_created to room: {room}")


async def emit_api_key_revoked(user_id, data):
    """Emit API key revoked event to user"""
    room = f"api_keys_{user_id}"
    await sio.emit('api_key_revoked', data, room=room)
    logger.info(f"Emitted api_key_revoked to room: {room}")


async def emit_api_key_used(user_id, data):
    """Emit API key used event to user"""
    room = f"api_keys_{user_id}"
    await sio.emit('api_key_used', data, room=room)
    logger.info(f"Emitted api_key_used to room: {room}")


async def emit_transaction_update(user_id, data):
    """Emit transaction update to user"""
    room = f"dashboard_{user_id}"
    await sio.emit('transaction_update', data, room=room)
    logger.info(f"Emitted transaction_update to room: {room}")


async def emit_analytics_update(user_id, data):
    """Emit analytics update to user"""
    room = f"dashboard_{user_id}"
    await sio.emit('analytics_update', data, room=room)
    logger.info(f"Emitted analytics_update to room: {room}")


async def emit_transaction_new(user_id, data):
    """Emit new transaction event to user"""
    room = f"transactions_{user_id}"
    await sio.emit('transaction:new', data, room=room)
    logger.info(f"Emitted transaction:new to room: {room}")


async def emit_transaction_status_update(user_id, data):
    """Emit transaction status update to user"""
    room = f"transactions_{user_id}"
    await sio.emit('transaction:update', data, room=room)
    logger.info(f"Emitted transaction:update to room: {room}")
