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

# Always run migrations since we're using SQLite
echo "Running migrations with SQLite database..."
python manage.py migrate --noinput || echo "Migration failed - will retry during startup"

# Create superuser if not exists (optional and only if env vars are set)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || echo "Superuser creation failed - may already exist"
fi
