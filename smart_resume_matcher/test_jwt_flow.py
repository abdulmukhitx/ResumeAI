#!/usr/bin/env python
"""
Debug script to test JWT authentication flow
"""

import os
import sys
import django
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_jwt_flow():
    """Test JWT authentication flow"""
    print("=" * 60)
    print("TESTING JWT AUTHENTICATION FLOW")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Access homepage
    print("\n1. Testing homepage access:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Homepage accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Homepage failed: {e}")
        return
    
    # Test 2: Try accessing JWT upload page without auth
    print("\n2. Testing JWT upload page (unauthenticated):")
    try:
        response = requests.get(f"{base_url}/jwt-resume-upload/")
        print(f"   Status: {response.status_code}")
        if "authentication" in response.text.lower() or "login" in response.text.lower():
            print("   ✅ Properly shows guest content for unauthenticated users")
        else:
            print("   ⚠️  May allow unauthenticated access")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Try accessing jobs page without auth
    print("\n3. Testing jobs page (unauthenticated):")
    try:
        response = requests.get(f"{base_url}/jobs/", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ Redirects to: {redirect_url}")
            if "login" in redirect_url:
                print("   ✅ Correctly redirects to login")
            else:
                print("   ⚠️  Unexpected redirect target")
        elif response.status_code == 200:
            print("   ⚠️  Jobs page accessible without authentication")
        else:
            print(f"   ❌ Unexpected response")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 4: Check login page
    print("\n4. Testing login page:")
    try:
        response = requests.get(f"{base_url}/login/")
        print(f"   ✅ Login page accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Login page failed: {e}")
    
    # Test 5: Check API endpoints
    print("\n5. Testing API endpoints:")
    try:
        response = requests.get(f"{base_url}/api/auth/user/")
        print(f"   API user endpoint: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ API properly requires authentication")
        else:
            print("   ⚠️  API may not require authentication")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
    
    print("\n" + "=" * 60)
    print("JWT AUTHENTICATION FLOW TEST COMPLETED")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS TO TEST:")
    print("1. Open browser and go to http://localhost:8000")
    print("2. Register/Login with your account")
    print("3. Upload a resume")
    print("4. Click 'Browse Job Matches' button")
    print("5. Check if you're redirected to login or see jobs page")

if __name__ == "__main__":
    test_jwt_flow()
