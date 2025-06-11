#!/bin/bash
# Production deployment script for Render

echo "=== SMART RESUME MATCHER DEPLOYMENT ==="
echo "Starting production deployment process..."

# 1. Set production environment variables
export DJANGO_SETTINGS_MODULE=config.settings
export PYTHONPATH="/opt/render/project/src/smart_resume_matcher:$PYTHONPATH"

# 2. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 3. Collect static files
echo "Collecting static files..."
cd smart_resume_matcher
python manage.py collectstatic --noinput

# 4. Run database migrations
echo "Running database migrations..."
python manage.py migrate

# 5. Create superuser if needed (skip if exists)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin@smartresumematcher.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# 6. Sync usernames
echo "Syncing usernames..."
python manage.py sync_usernames

# 7. Test AI functionality
echo "Testing AI functionality..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import AIAnalyzer
try:
    analyzer = AIAnalyzer()
    result = analyzer.analyze_resume('Test resume with Python skills')
    print('✅ AI Analysis working in production')
    print(f'Sample result: {result}')
except Exception as e:
    print(f'❌ AI Analysis error: {e}')
"

# 8. Check database health
echo "Checking database health..."
python check_database_health.py

echo "=== DEPLOYMENT COMPLETED ==="
echo "Application should be ready at your Render URL"
