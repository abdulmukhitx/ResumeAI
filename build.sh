#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Starting build process at repository root"

# Check if we're in the repository root or the project directory
if [ -d "smart_resume_matcher" ]; then
  echo "==> Found smart_resume_matcher directory, using nested project structure"
  cd smart_resume_matcher
fi

echo "==> Current directory: $(pwd)"
echo "==> Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

# Set up SQLite database persistence if running on Render
if [ -d "/var/data" ]; then
  echo "==> Render environment detected, setting up SQLite persistence..."
  if [ -f "./setup_sqlite_persistence.sh" ]; then
    bash ./setup_sqlite_persistence.sh
  fi
fi

# Always run migrations since we're using SQLite
echo "==> Running migrations with SQLite database..."
python manage.py migrate --noinput || echo "Migration failed - will retry during startup"

echo "==> Build process completed"
