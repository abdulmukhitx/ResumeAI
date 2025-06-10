#!/usr/bin/env bash
# exit on error
set -o errexit

# Check if we're in the repository root or the project directory
if [ -d "smart_resume_matcher" ]; then
  echo "==> Found smart_resume_matcher directory, using nested project structure"
  cd smart_resume_matcher
fi

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if not exists (optional)
# python manage.py createsuperuser --no-input
