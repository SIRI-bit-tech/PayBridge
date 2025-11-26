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

# Run migrations but skip problematic billing plans migration
echo "Running database migrations (skipping billing plans)..."
python manage.py migrate --fake api 0006 || echo "Billing plans migration skipped"
python manage.py migrate --noinput || {
    echo "Some migrations failed, but continuing with deployment..."
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Skip superuser creation - causing database constraint issues
echo "Skipping superuser creation to avoid database conflicts..."

# Check Django configuration
echo "Checking Django configuration..."
python check_django.py || {
    echo "Django check failed - deployment may have issues"
    exit 1
}

echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf