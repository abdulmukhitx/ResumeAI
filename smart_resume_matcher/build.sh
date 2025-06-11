#!/usr/bin/env bash
# exit on error
set -o errexit

# Move to the correct directory if not in a nested project structure
if [ -d "smart_resume_matcher" ]; then
  cd smart_resume_matcher
fi

echo "Current directory: $(pwd)"
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Check if DATABASE_URL is available
if [ -z "$DATABASE_URL" ]; then
  echo "WARNING: No DATABASE_URL found, skipping migrations"
else
  echo "DATABASE_URL is set. Will attempt migrations after a short delay..."
  # Add a delay to ensure database is fully available
  sleep 5
  
  # Test database connection before migrating
  echo "Testing database connection..."
  python -c "
import sys
import os
import django
import dj_database_url
import psycopg2
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
db_url = os.environ.get('DATABASE_URL')
db_config = dj_database_url.parse(db_url)
try:
    conn = psycopg2.connect(
        dbname=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
        host=db_config['HOST'],
        port=db_config['PORT']
    )
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection error: {e}')
    # Don't exit with error to allow build to complete
    # The web process will retry migrations
" || echo "Database connection test failed, but continuing build process"

  # Run migrations with retry logic
  echo "Running migrations..."
  python manage.py migrate --noinput || echo "Migrations failed - the web process will retry on startup"
fi

# Create superuser if not exists (optional and only if env vars are set)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || echo "Superuser creation failed - may already exist"
fi
