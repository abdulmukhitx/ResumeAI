#!/bin/bash

# Test deployment locally before Railway
echo "🧪 Testing deployment locally"
echo "==============================="

cd /home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher

# Use minimal requirements
if [ -f "requirements_minimal.txt" ]; then
    echo "📦 Installing minimal requirements..."
    pip install -r requirements_minimal.txt
fi

# Test if Django can start
echo "🔧 Testing Django configuration..."
python manage.py check --deploy

# Test if migrations work
echo "🗄️  Testing migrations..."
python manage.py makemigrations --dry-run

# Test if static files can be collected
echo "📁 Testing static files collection..."
python manage.py collectstatic --noinput --dry-run

# Test if basic imports work
echo "🐍 Testing Python imports..."
python -c "
import django
from django.conf import settings
from config.settings import *
print('✅ Django imports successful')
print(f'✅ DEBUG: {DEBUG}')
print(f'✅ ALLOWED_HOSTS: {ALLOWED_HOSTS}')
print(f'✅ Database: {DATABASES[\"default\"][\"ENGINE\"]}')
"

echo ""
echo "✅ Local deployment test complete!"
echo "If no errors appeared above, the deployment should work on Railway."
