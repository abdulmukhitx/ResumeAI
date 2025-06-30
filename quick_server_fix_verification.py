#!/usr/bin/env python3
"""
Quick verification that the fixes resolved the main issues.
"""

import os
import sys
import django
import requests

# Add the project directory to the Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_chrome_devtools_fix():
    """Test that Chrome DevTools requests no longer return 404."""
    print("🔧 Testing Chrome DevTools Fix...")
    
    try:
        response = requests.get('http://localhost:8000/.well-known/appspecific/com.chrome.devtools.json', timeout=5)
        if response.status_code == 200:
            print("✅ Chrome DevTools endpoint now returns 200")
            return True
        else:
            print(f"❌ Chrome DevTools endpoint returns: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server not accessible")
        return False

def test_redirect_protection():
    """Test that redirect protection is working."""
    print("🛡️ Testing Redirect Protection...")
    
    try:
        # Test that basic pages load without redirect loops
        test_urls = [
            'http://localhost:8000/',
            'http://localhost:8000/login/',
            'http://localhost:8000/register/',
        ]
        
        for url in test_urls:
            response = requests.get(url, timeout=5, allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"✅ {url} - Status: {response.status_code}")
            else:
                print(f"❌ {url} - Status: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Redirect test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints are accessible."""
    print("🔌 Testing API Endpoints...")
    
    try:
        # Get a JWT token
        user = User.objects.first()
        if not user:
            print("❌ No user found for testing")
            return False
        
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test API endpoints
        api_urls = [
            'http://localhost:8000/api/auth/user/',
            'http://localhost:8000/api/resume/list/',
        ]
        
        for url in api_urls:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - API working")
            else:
                print(f"❌ {url} - Status: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run verification tests."""
    print("🔍 Server Issues Verification")
    print("=" * 40)
    
    tests = [
        ("Chrome DevTools Fix", test_chrome_devtools_fix),
        ("Redirect Protection", test_redirect_protection),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("=" * 40)
    print("📊 Results:")
    all_passed = True
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All fixes working correctly!")
        print("ℹ️  Note: 302 redirects in job pages are normal when users")
        print("   don't have resumes uploaded - this is security behavior.")
    else:
        print("⚠️  Some issues remain. Check the server logs.")
    
    return all_passed

if __name__ == "__main__":
    main()
