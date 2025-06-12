#!/usr/bin/env python
"""
Production Deployment Sync Script
Ensures the production deployment environment matches the working local environment
"""
import os
import sys
import django
import json
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.models import Resume
from accounts.models import User
from jobs.models import JobMatch
from django.core.management import call_command
from django.core import management
from django.utils import timezone

def create_production_data_backup():
    """Create a backup of the current working data for production deployment"""
    print("=== CREATING PRODUCTION DATA BACKUP ===\n")
    
    # Create backup directory
    backup_dir = Path("deployment_backup")
    backup_dir.mkdir(exist_ok=True)
    
    # Backup database data
    backup_file = backup_dir / f"production_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("1. BACKING UP DATABASE DATA:")
    try:
        with open(backup_file, 'w') as f:
            management.call_command('dumpdata', 
                                    '--natural-foreign', 
                                    '--natural-primary',
                                    '--indent=2',
                                    stdout=f)
        print(f"   ✅ Data backed up to: {backup_file}")
    except Exception as e:
        print(f"   ❌ Backup error: {e}")
        return None
    
    # Create deployment manifest
    manifest = {
        'timestamp': str(timezone.now()),
        'users_count': User.objects.count(),
        'resumes_count': Resume.objects.count(),
        'completed_resumes': Resume.objects.filter(status='completed').count(),
        'job_matches_count': JobMatch.objects.count(),
        'backup_file': str(backup_file),
        'verified_user': {
            'email': 'asalachik@gmail.com',
            'has_resume': Resume.objects.filter(user__email='asalachik@gmail.com').exists(),
            'active_resume_status': 'completed' if Resume.objects.filter(user__email='asalachik@gmail.com', is_active=True).exists() else 'none'
        }
    }
    
    manifest_file = backup_dir / "deployment_manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   ✅ Deployment manifest created: {manifest_file}")
    print(f"   Users: {manifest['users_count']}")
    print(f"   Resumes: {manifest['resumes_count']}")
    print(f"   Completed resumes: {manifest['completed_resumes']}")
    
    return backup_file, manifest_file

def prepare_production_environment():
    """Prepare environment for production deployment"""
    print("\n=== PREPARING PRODUCTION ENVIRONMENT ===\n")
    
    # 1. Update environment configuration
    print("1. UPDATING ENVIRONMENT CONFIGURATION:")
    
    env_config = {
        'DJANGO_SETTINGS_MODULE': 'config.settings',
        'DEBUG': 'False',
        'ALLOWED_HOSTS': '*',  # Will be updated in production
        'DATABASE_URL': 'sqlite:////var/data/db.sqlite3',  # Production SQLite path
        'PYTHONPATH': '/opt/render/project/src/smart_resume_matcher'
    }
    
    for key, value in env_config.items():
        print(f"   {key}={value}")
    
    # 2. Create production-ready settings
    print("\n2. CREATING PRODUCTION SETTINGS:")
    production_settings = """
# Production deployment settings
import os
from .settings import *

# Override for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Update with actual domain

# Database persistence for Render
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600)

# Static files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'resumes': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
"""
    
    settings_file = Path("config/production_settings.py")
    with open(settings_file, 'w') as f:
        f.write(production_settings)
    
    print(f"   ✅ Production settings created: {settings_file}")
    
    return True

def create_deployment_script():
    """Create comprehensive deployment script for Render"""
    print("\n=== CREATING DEPLOYMENT SCRIPT ===\n")
    
    deployment_script = '''#!/bin/bash
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

# Navigate to project directory
echo "1. NAVIGATING TO PROJECT DIRECTORY"
if [ -d "smart_resume_matcher" ]; then
    cd smart_resume_matcher
    check_success "Directory navigation"
else
    echo "❌ smart_resume_matcher directory not found"
    exit 1
fi

# Set up SQLite persistence for Render
echo "2. SETTING UP DATABASE PERSISTENCE"
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
echo "3. COLLECTING STATIC FILES"
python manage.py collectstatic --noinput
check_success "Static files collection"

# Create superuser if needed
echo "4. CHECKING SUPERUSER"
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
echo "5. SYNCING USER DATA"
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
    print(f'Skills found: {len(result.get(\"skills\", []))}')
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
        print(f'User asalachik@gmail.com: Resume \"{resume.original_filename}\" with {len(resume.extracted_skills)} skills')
    else:
        print('User asalachik@gmail.com: No active resume found')
except User.DoesNotExist:
    print('User asalachik@gmail.com: Not found in database')
"
check_success "Deployment verification"

echo "=== DEPLOYMENT COMPLETED SUCCESSFULLY ==="
echo "Application is ready to start"
'''
    
    deploy_script = Path("../render_deploy.sh")
    with open(deploy_script, 'w') as f:
        f.write(deployment_script)
    
    # Make executable
    os.chmod(deploy_script, 0o755)
    
    print(f"   ✅ Deployment script created: {deploy_script}")
    return deploy_script

def update_render_configuration():
    """Update render.yaml for production deployment"""
    print("\n=== UPDATING RENDER CONFIGURATION ===\n")
    
    render_config = """services:
  - type: web
    name: smart-resume-matcher
    env: python
    buildCommand: ./render_deploy.sh
    startCommand: ./start.sh
    disk:
      name: smart-resume-data
      mountPath: /var/data
      sizeGB: 1
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: "*"
      - key: GROQ_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings
      - key: PYTHONPATH
        value: "/opt/render/project/src/smart_resume_matcher"
      - key: DATABASE_URL
        value: "sqlite:////var/data/db.sqlite3"
"""
    
    render_file = Path("../render.yaml")
    with open(render_file, 'w') as f:
        f.write(render_config)
    
    print(f"   ✅ Render configuration updated: {render_file}")
    return render_file

def main():
    """Main deployment sync function"""
    print("Starting production deployment synchronization...\n")
    
    try:
        # Step 1: Create backup of working data
        backup_file, manifest_file = create_production_data_backup()
        if not backup_file:
            print("❌ Failed to create backup, aborting deployment")
            return False
        
        # Step 2: Prepare production environment
        prepare_production_environment()
        
        # Step 3: Create deployment script
        deploy_script = create_deployment_script()
        
        # Step 4: Update Render configuration
        render_file = update_render_configuration()
        
        print("\n=== DEPLOYMENT SYNC COMPLETED ===\n")
        print("🎯 NEXT STEPS FOR RENDER DEPLOYMENT:")
        print("1. Push these changes to your Git repository")
        print("2. In Render dashboard, update your web service:")
        print("   - Build Command: ./render_deploy.sh")
        print("   - Start Command: ./start.sh")
        print("3. Set environment variables in Render:")
        print("   - GROQ_API_KEY: (your API key)")
        print("   - DEBUG: false")
        print("   - ALLOWED_HOSTS: your-app.onrender.com")
        print("4. Deploy the service")
        print("\n📁 FILES CREATED:")
        print(f"   - {backup_file}")
        print(f"   - {manifest_file}")
        print(f"   - {deploy_script}")
        print(f"   - {render_file}")
        print(f"   - config/production_settings.py")
        
        print(f"\n✅ The production deployment should now match your local environment with:")
        print(f"   - {User.objects.count()} users")
        print(f"   - {Resume.objects.count()} resumes")
        print(f"   - Working resume analysis for user 'asalachik@gmail.com'")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment sync failed: {e}")
        return False

if __name__ == "__main__":
    main()
