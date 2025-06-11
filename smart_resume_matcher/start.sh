#!/usr/bin/env bash
set -o errexit

echo "Starting application..."

# Set up SQLite database persistence if running on Render
if [ -d "/var/data" ]; then
  echo "Render environment detected, setting up SQLite persistence..."
  ./setup_sqlite_persistence.sh
fi

# Always run migrations with SQLite
echo "Running migrations on startup with SQLite database..."
python manage.py migrate --noinput

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
