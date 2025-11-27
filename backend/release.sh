#!/bin/bash
set -e

echo "Starting PayBridge Heroku Release..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

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

echo "✓ Release tasks completed successfully!"