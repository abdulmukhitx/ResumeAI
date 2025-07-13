#!/bin/bash
set -e

echo "Starting ABSOLUTE MINIMAL Django deployment"

# Use absolute minimal settings
export DJANGO_SETTINGS_MODULE=config.absolute_settings

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" || true
else
    echo "Creating default superuser..."
    python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser created: admin / admin123')
else:
    print('✅ Superuser already exists')
" || true
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Start server
echo "Starting server..."
exec gunicorn config.absolute_wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
