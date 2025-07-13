#!/bin/bash
# Railway build script

set -e

echo "Starting Railway deployment build..."

# Upgrade pip and core tools
echo "Upgrading pip and core tools..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

echo "Build completed successfully!"
