#!/bin/bash

# PayBridge ASGI Server Startup Script

echo "Starting PayBridge with WebSocket support..."

# Check if daphne is installed
if ! python -c "import daphne" 2>/dev/null; then
    echo "Daphne not found. Installing..."
    pip install daphne
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start the server
echo "Starting Daphne server on port 8000..."
daphne -b 0.0.0.0 -p 8000 paybridge.asgi:application
