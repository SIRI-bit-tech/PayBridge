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

# First, try normal migration
if python manage.py migrate --noinput; then
    echo "Migrations completed successfully"
else
    echo "Normal migration failed, trying to resolve conflicts..."
    
    # Check if tables exist and mark initial migrations as fake
    echo "Marking initial migrations as applied..."
    python manage.py migrate --fake-initial --noinput || true
    
    # Try to run remaining migrations
    echo "Running remaining migrations..."
    python manage.py migrate --noinput || {
        echo "Some migrations failed, but continuing with deployment..."
    }
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Initialize plans (one time setup)
echo "Initializing plans..."
python init_plans.py || echo "Plans initialization completed or already exists"

# Create superuser (required for admin access)
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME:-admin}'
email = '${DJANGO_SUPERUSER_EMAIL:-admin@paybridge.com}'
password = '${DJANGO_SUPERUSER_PASSWORD:-admin123}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
"

echo "Starting services with supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf