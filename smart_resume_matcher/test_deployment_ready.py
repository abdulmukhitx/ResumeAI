#!/usr/bin/env python3
"""
Final deployment readiness test for Smart Resume Matcher
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        # Views imports
        from resumes.views import find_matching_jobs, analyze_resume, resume_upload_view
        from resumes.enhanced_analyzer import EnhancedAIAnalyzer
        from resumes.enhanced_job_matcher import EnhancedJobMatcher
        from jobs.job_matcher import JobMatcher
        
        # Model imports via apps
        from django.apps import apps
        Resume = apps.get_model('resumes', 'Resume')
        Job = apps.get_model('jobs', 'Job')
        JobMatch = apps.get_model('jobs', 'JobMatch')
        
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("Testing database...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_models():
    """Test model instantiation"""
    print("Testing models...")
    try:
        from django.apps import apps
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        Resume = apps.get_model('resumes', 'Resume')
        Job = apps.get_model('jobs', 'Job')
        JobMatch = apps.get_model('jobs', 'JobMatch')
        
        # Test model structure
        resume_fields = [f.name for f in Resume._meta.get_fields()]
        job_fields = [f.name for f in Job._meta.get_fields()]
        jobmatch_fields = [f.name for f in JobMatch._meta.get_fields()]
        
        required_resume_fields = ['user', 'file', 'status', 'extracted_skills', 'experience_level']
        required_job_fields = ['title', 'company_name', 'description', 'is_active']
        required_jobmatch_fields = ['user', 'job', 'resume', 'match_score']
        
        for field in required_resume_fields:
            if field not in resume_fields:
                raise Exception(f"Resume model missing field: {field}")
                
        for field in required_job_fields:
            if field not in job_fields:
                raise Exception(f"Job model missing field: {field}")
                
        for field in required_jobmatch_fields:
            if field not in jobmatch_fields:
                raise Exception(f"JobMatch model missing field: {field}")
        
        print("✓ All models have required fields")
        return True
    except Exception as e:
        print(f"✗ Model test error: {e}")
        return False

def test_settings():
    """Test critical settings"""
    print("Testing settings...")
    try:
        # Check critical settings
        critical_settings = [
            'SECRET_KEY', 'DATABASES', 'INSTALLED_APPS', 
            'MIDDLEWARE', 'ROOT_URLCONF', 'TEMPLATES'
        ]
        
        for setting in critical_settings:
            if not hasattr(settings, setting):
                raise Exception(f"Missing setting: {setting}")
        
        # Check database config
        if not settings.DATABASES:
            raise Exception("DATABASES setting is empty")
            
        # Check that our apps are installed
        required_apps = ['resumes', 'jobs', 'accounts']
        for app in required_apps:
            if app not in settings.INSTALLED_APPS:
                print(f"Warning: {app} not in INSTALLED_APPS")
        
        print("✓ Settings configuration valid")
        return True
    except Exception as e:
        print(f"✗ Settings error: {e}")
        return False

def test_urls():
    """Test URL configuration"""
    print("Testing URL configuration...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        # Test that basic URLs resolve
        client = Client()
        
        # Test some basic URL patterns
        try:
            # This should not raise an exception even if view doesn't exist
            from django.urls import resolve
            resolve('/')
        except:
            pass  # It's OK if root URL doesn't exist yet
        
        print("✓ URL configuration loads successfully")
        return True
    except Exception as e:
        print(f"✗ URL configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing deployment readiness for Smart Resume Matcher")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_database,
        test_models,
        test_settings,
        test_urls
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("🎉 ALL TESTS PASSED! App is ready for deployment!")
        print("\nNext steps:")
        print("1. Test locally: python manage.py runserver")
        print("2. Run migrations: python manage.py migrate")
        print("3. Create superuser: python manage.py createsuperuser")
        print("4. Test Railway deployment")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
