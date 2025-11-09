@echo off
REM PayBridge ASGI Server Startup Script for Windows

echo Starting PayBridge with WebSocket support...

REM Check if daphne is installed
python -c "import daphne" 2>nul
if errorlevel 1 (
    echo Daphne not found. Installing...
    pip install daphne
)

REM Run migrations
echo Running migrations...
python manage.py migrate

REM Start the server
echo Starting Daphne server on port 8000...
daphne -b 0.0.0.0 -p 8000 paybridge.asgi:application
