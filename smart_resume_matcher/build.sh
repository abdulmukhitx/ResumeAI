#!/usr/bin/env bash
# exit on error
set -o errexit

# Move to the correct directory
cd smart_resume_matcher

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if not exists (optional)
# python manage.py createsuperuser --no-input
