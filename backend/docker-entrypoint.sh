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

# Run database migrations with conflict handling
echo "Running database migrations..."

# Check if billing_plans table exists and handle accordingly
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute(\"SELECT 1 FROM billing_plans LIMIT 1;\")
    print('billing_plans table exists, marking migration as fake')
    exit(1)
except:
    print('billing_plans table does not exist, proceeding with normal migration')
    exit(0)
" && BILLING_EXISTS=false || BILLING_EXISTS=true

if [ "$BILLING_EXISTS" = "true" ]; then
    echo "Billing tables exist, using fake migration strategy..."
    # Mark the problematic migration as fake
    python manage.py migrate api 0006 --fake --noinput || true
    # Run remaining migrations
    python manage.py migrate --noinput || {
        echo "Some migrations failed, but continuing with deployment..."
    }
else
    echo "Running normal migrations..."
    python manage.py migrate --noinput || {
        echo "Migration failed, trying fake-initial approach..."
        python manage.py migrate --fake-initial --noinput || true
        python manage.py migrate --noinput || {
            echo "Some migrations failed, but continuing with deployment..."
        }
    }
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (required for admin access)
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME:-admin}'
email = '${DJANGO_SUPERUSER_EMAIL:-admin@paybridge.com}'
password = '${DJANGO_SUPERUSER_PASSWORD:-admin123}'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(username, email, password)
    user.last_login = timezone.now()
    user.save()
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
"

# Initialize plans (after migrations and superuser creation)
echo "Initializing billing plans..."
python init_plans.py || echo "Plans initialization completed or already exists"

echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf