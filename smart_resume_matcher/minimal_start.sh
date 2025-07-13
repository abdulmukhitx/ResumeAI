#!/bin/bash
set -e

echo "Starting Smart Resume Matcher - Minimal Deployment"

# Use minimal settings
export DJANGO_SETTINGS_MODULE=config.minimal_settings
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser
echo "Creating superuser..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('✅ Superuser created: admin@example.com / admin123')
else:
    print('✅ Superuser already exists')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level info
