#!/bin/bash
# Railway custom build command

set -e

echo "🚀 Railway Build Process Starting..."

# Upgrade pip and essential tools
echo "📦 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build process completed successfully!"
