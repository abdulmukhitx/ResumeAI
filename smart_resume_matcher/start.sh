#!/usr/bin/env bash
set -o errexit

echo "Starting application..."

# Handle migrations at startup to ensure the database is ready
if [ -n "$DATABASE_URL" ]; then
  echo "Running migrations on startup to ensure database is ready..."
  python manage.py migrate --noinput
else
  echo "WARNING: DATABASE_URL not set, skipping migrations"
fi

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
