#!/usr/bin/env bash
set -o errexit

echo "Starting application..."

# Find the correct directory structure
if [ -d "smart_resume_matcher" ]; then
  echo "Found smart_resume_matcher directory, changing to it"
  cd smart_resume_matcher
fi

# Set up SQLite database persistence if running on Render
if [ -d "/var/data" ]; then
  echo "Render environment detected, setting up SQLite persistence..."
  if [ -f "./setup_sqlite_persistence.sh" ]; then
    bash ./setup_sqlite_persistence.sh
  fi
fi

# Run migrations
echo "Running migrations with SQLite database..."
python manage.py migrate --noinput

# Start gunicorn with the correct WSGI path
echo "Starting gunicorn with config.wsgi..."
# This is the critical line that tells Gunicorn how to find your WSGI application
gunicorn --log-file=- config.wsgi:application --bind 0.0.0.0:$PORT
