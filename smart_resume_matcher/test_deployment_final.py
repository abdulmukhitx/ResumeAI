#!/usr/bin/env python3
"""
Final deployment test script for Railway deployment
"""
import os
import sys
import django
from pathlib import Path

# Add the current directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def test_basic_django_setup():
    """Test basic Django setup"""
    print("🔧 Testing Django setup...")
    
    try:
        django.setup()
        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_import_apps():
    """Test importing Django apps"""
    print("📦 Testing app imports...")
    
    try:
        from django.apps import apps
        app_configs = apps.get_app_configs()
        print(f"✅ Found {len(app_configs)} apps:")
        for app in app_configs:
            print(f"   - {app.name}")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_database_config():
    """Test database configuration"""
    print("🗄️  Testing database configuration...")
    
    try:
        from django.conf import settings
        db_config = settings.DATABASES.get('default')
        if not db_config:
            print("❌ No default database configuration found")
            return False
            
        engine = db_config.get('ENGINE', 'Unknown')
        print(f"✅ Database engine: {engine}")
        
        if 'postgresql' in engine.lower():
            print("✅ PostgreSQL configured for production")
        elif 'sqlite' in engine.lower():
            print("✅ SQLite configured for development")
        
        return True
    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        return False

def test_static_files():
    """Test static files configuration"""
    print("📁 Testing static files configuration...")
    
    try:
        from django.conf import settings
        
        print(f"✅ STATIC_URL: {settings.STATIC_URL}")
        print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"✅ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        
        return True
    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False

def test_security_settings():
    """Test security settings"""
    print("🔒 Testing security settings...")
    
    try:
        from django.conf import settings
        
        secret_key = settings.SECRET_KEY
        if len(secret_key) >= 50:
            print("✅ SECRET_KEY length is adequate")
        else:
            print(f"⚠️  SECRET_KEY might be too short ({len(secret_key)} chars)")
        
        if 'django-insecure' in secret_key:
            print("⚠️  SECRET_KEY contains 'django-insecure' prefix")
        else:
            print("✅ SECRET_KEY looks secure")
        
        if settings.ALLOWED_HOSTS:
            print(f"✅ ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
        else:
            print("⚠️  ALLOWED_HOSTS is empty")
        
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        
        return True
    except Exception as e:
        print(f"❌ Security settings test failed: {e}")
        return False

def test_wsgi_app():
    """Test WSGI application"""
    print("🌐 Testing WSGI application...")
    
    try:
        from config.wsgi import application
        print("✅ WSGI application imported successfully")
        return True
    except Exception as e:
        print(f"❌ WSGI application test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 Running final deployment tests...\n")
    
    tests = [
        test_basic_django_setup,
        test_import_apps,
        test_database_config,
        test_static_files,
        test_security_settings,
        test_wsgi_app,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}\n")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"🏁 Deployment Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment!")
    else:
        print("⚠️  Some tests failed. Please fix issues before deploying.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
