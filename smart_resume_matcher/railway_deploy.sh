#!/bin/bash

# Railway Deployment Script for Smart Resume Matcher
echo "🚀 Railway Deployment Script"
echo "=============================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations resumes  
python manage.py makemigrations jobs
python manage.py makemigrations notifications
python manage.py makemigrations core
python manage.py migrate

# Create superuser if doesn't exist
echo "👤 Creating superuser if needed..."
python manage.py shell -c "
from accounts.models import User
import os

# Try to create superuser from environment variables
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@admin.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'adminpass123')

if not User.objects.filter(email=admin_email).exists():
    User.objects.create_superuser(
        email=admin_email,
        password=admin_password,
        username=admin_email,
        first_name='Admin',
        last_name='User'
    )
    print(f'✅ Superuser created: {admin_email}')
else:
    print(f'ℹ️ Superuser already exists: {admin_email}')
"

echo "🎉 Deployment preparation complete!"
echo "Starting application..."

# Start the application
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
