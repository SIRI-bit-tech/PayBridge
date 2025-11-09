# Running PayBridge with WebSocket Support

The PayBridge backend requires ASGI server support for WebSocket connections.

## Option 1: Using Daphne (Recommended for Development)

```bash
# Install Daphne if not already installed
pip install daphne

# Run the server
daphne -b 0.0.0.0 -p 8000 paybridge.asgi:application
```

## Option 2: Using Uvicorn

```bash
# Install Uvicorn if not already installed
pip install uvicorn

# Run the server
uvicorn paybridge.asgi:application --host 0.0.0.0 --port 8000 --reload
```

## Testing WebSocket Connection

Once the server is running with ASGI support, you can test the WebSocket connection:

1. Login to get an access token
2. Connect to: `ws://localhost:8000/ws/dashboard/?token=YOUR_ACCESS_TOKEN`
3. The dashboard will automatically connect and receive real-time updates

## Note

The standard Django development server (`python manage.py runserver`) does NOT support WebSockets.
You must use Daphne or Uvicorn for WebSocket functionality.
