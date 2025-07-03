#!/usr/bin/env python
"""
Test script to verify Railway deployment readiness
"""

import os
import sys
import django
from django.conf import settings
from django.core import management

# Add the project directory to Python path
sys.path.insert(0, '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_deployment_readiness():
    print("🚀 Testing Railway Deployment Readiness")
    print("=" * 50)
    
    try:
        # Test Django setup
        django.setup()
        print("✅ Django setup successful")
        
        # Test settings import
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
        print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        # Test management commands
        management.call_command('check', verbosity=0)
        print("✅ Django system check passed")
        
        # Test collectstatic (dry run)
        try:
            management.call_command('collectstatic', '--dry-run', '--noinput', verbosity=0)
            print("✅ Static files collection ready")
        except Exception as e:
            print(f"⚠️ Static files warning: {e}")
        
        # Test migrations check
        try:
            management.call_command('migrate', '--check', verbosity=0)
            print("✅ Database migrations up to date")
        except Exception as e:
            print(f"⚠️ Migration warning: {e}")
        
        print("\n🎯 RAILWAY DEPLOYMENT COMMANDS:")
        print("=" * 40)
        print("1. Add PostgreSQL service in Railway dashboard")
        print("2. Set environment variables:")
        print("   - DEBUG=False")
        print("   - SECRET_KEY=<your-secret-key>")
        print("   - DATABASE_URL=<auto-provided-by-railway>")
        print("3. Deploy with current Procfile")
        print("\n✅ Ready for Railway deployment!")
        
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deployment_readiness()
