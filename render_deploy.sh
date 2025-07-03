#!/bin/bash
# Comprehensive production deployment script for Render

echo "=== SMART RESUME MATCHER PRODUCTION DEPLOYMENT ==="
echo "Starting deployment at $(date)"

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings
export PYTHONPATH="/opt/render/project/src/smart_resume_matcher:$PYTHONPATH"

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 completed successfully"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

# Install Python dependencies
echo "1. INSTALLING PYTHON DEPENDENCIES"
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
    check_success "Root requirements installation"
fi
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    check_success "Local requirements installation"
fi

# Navigate to project directory
echo "2. NAVIGATING TO PROJECT DIRECTORY"
if [ -d "smart_resume_matcher" ]; then
    cd smart_resume_matcher
    check_success "Directory navigation"
else
    echo "Already in smart_resume_matcher directory or current directory is correct"
fi

# Set up SQLite persistence for Render
echo "3. SETTING UP DATABASE PERSISTENCE"
if [ -d "/var/data" ]; then
    echo "Render environment detected, setting up SQLite persistence..."
    mkdir -p /var/data
    
    # Create database if it doesn't exist
    if [ ! -f "/var/data/db.sqlite3" ]; then
        echo "Creating new SQLite database..."
        python manage.py migrate --noinput
        check_success "Initial database creation"
        
        # Load production data if backup exists
        if [ -f "deployment_backup/production_data_*.json" ]; then
            echo "Loading production data..."
            python manage.py loaddata deployment_backup/production_data_*.json
            check_success "Data loading"
        fi
    else
        echo "Existing database found, running migrations..."
        python manage.py migrate --noinput
        check_success "Database migrations"
    fi
else
    echo "Local environment detected, using local SQLite..."
    python manage.py migrate --noinput
    check_success "Local database migrations"
fi

# Collect static files
echo "4. COLLECTING STATIC FILES"
python manage.py collectstatic --noinput
check_success "Static files collection"

# Create superuser if needed
echo "5. CHECKING SUPERUSER"
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
check_success "Superuser check"

# Sync usernames
echo "6. SYNCING USER DATA"
python manage.py sync_usernames
check_success "Username synchronization"

# Test AI functionality
echo "6. TESTING AI FUNCTIONALITY"
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import AIAnalyzer
try:
    analyzer = AIAnalyzer()
    result = analyzer.analyze_resume('Test resume with Python and Django skills')
    print('✅ AI Analysis working')
    print(f'Skills found: {len(result.get("skills", []))}')
except Exception as e:
    print(f'❌ AI Analysis error: {e}')
    exit 1
"
check_success "AI functionality test"

# Verify deployment status
echo "7. DEPLOYMENT VERIFICATION"
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from resumes.models import Resume

users = User.objects.count()
resumes = Resume.objects.count()
completed = Resume.objects.filter(status='completed').count()

print(f'Users in database: {users}')
print(f'Total resumes: {resumes}')
print(f'Completed resumes: {completed}')

# Check specific user
try:
    user = User.objects.get(email='asalachik@gmail.com')
    user_resumes = Resume.objects.filter(user=user, is_active=True)
    if user_resumes.exists():
        resume = user_resumes.first()
        print(f'User asalachik@gmail.com: Resume "{resume.original_filename}" with {len(resume.extracted_skills)} skills')
    else:
        print('User asalachik@gmail.com: No active resume found')
except User.DoesNotExist:
    print('User asalachik@gmail.com: Not found in database')
"
check_success "Deployment verification"

echo "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo "Application is ready to start"
