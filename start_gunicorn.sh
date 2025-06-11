#!/usr/bin/env bash

# Exit on error
set -o errexit

# Navigate to project directory first - this is critical
if [ -d "smart_resume_matcher" ]; then
  cd smart_resume_matcher
  echo "Changed directory to $(pwd)"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start Gunicorn with explicitly named WSGI application
echo "Starting Gunicorn server..."
exec gunicorn --log-file=- config.wsgi:application --bind 0.0.0.0:$PORT
