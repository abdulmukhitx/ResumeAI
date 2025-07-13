#!/bin/bash
set -e

echo "Starting Smart Resume Matcher (SQLite)..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=config.settings

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if needed
echo "Creating superuser if needed..."
python manage.py shell << SHELL_EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created: admin@example.com / admin123')
else:
    print('Superuser already exists')
SHELL_EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
