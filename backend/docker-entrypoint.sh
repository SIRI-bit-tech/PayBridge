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

# Skip migrations entirely - database already exists
echo "Skipping migrations - using existing database schema..."
echo "Database schema assumed to be already set up"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (required for admin access)
echo "Creating superuser..."
export DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
export DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@paybridge.com}  
export DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin123}

python manage.py createsuperuser --noinput || echo "Superuser already exists or creation failed - continuing..."

# Initialize plans (after migrations and superuser creation)
echo "Initializing billing plans..."
python init_plans.py || echo "Plans initialization completed or already exists"

echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf