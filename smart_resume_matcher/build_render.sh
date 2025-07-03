#!/bin/bash
set -e

echo "Starting Render build process..."

# Upgrade pip first
python -m pip install --upgrade pip

# Install setuptools early to ensure pkg_resources is available
echo "Installing setuptools..."
pip install "setuptools>=75.0.0"

# Install system dependencies for PDF processing
echo "Installing system dependencies..."
apt-get update
apt-get install -y tesseract-ocr poppler-utils

# Install Python dependencies
echo "Installing Python requirements..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

echo "Build completed successfully!"
