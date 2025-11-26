#!/bin/bash
set -e

echo "Starting PayBridge Backend Deployment..."

# Check if DATABASE_URL is set (for cloud databases like Neon, we skip readiness check)
if [ -n "$DATABASE_URL" ]; then
    echo "Using cloud database (DATABASE_URL is set)"
    echo "Skipping database readiness check for cloud provider..."
else
    echo "No DATABASE_URL found, checking local database..."
    # Fallback to environment variables or defaults for local development
    DB_HOST=${DATABASE_HOST:-localhost}
    DB_PORT=${DATABASE_PORT:-5432}
    DB_USER=${DATABASE_USER:-postgres}
    
    # Wait for local database to be ready
    echo "Waiting for database at $DB_HOST:$DB_PORT..."
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "Database is ready!"
fi

# Run migrations with comprehensive error handling
echo "Running database migrations..."

# Use our simple migration script that handles all common issues
python simple_migrate.py

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@paybridge.com', 
        password='admin123'
    )
    print('✓ Superuser created: admin/admin123')
else:
    print('✓ Superuser already exists')
" || echo "⚠ Superuser creation skipped"

# Test Redis connection first
echo "Testing Redis connection..."
python test_redis_simple.py

# Check Django configuration
echo "Checking Django configuration..."
python check_django.py || {
    echo "⚠ Django check had warnings - continuing deployment"
    echo "Some features may be limited until Redis connection is stable"
}

echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf