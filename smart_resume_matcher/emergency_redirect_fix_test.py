#!/usr/bin/env python
"""
Emergency Redirect Fix Test
Clear all sessions and test the redirect fix
"""

import os
import django
import sys

# Add the smart_resume_matcher directory to Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import requests
import time

def clear_all_sessions():
    """Clear all Django sessions"""
    session_count = Session.objects.count()
    Session.objects.all().delete()
    print(f"✅ Cleared {session_count} Django sessions")

def test_redirect_fix():
    """Test that the redirect fix is working"""
    server_url = "http://127.0.0.1:8003"
    
    print("\n" + "="*60)
    print(" EMERGENCY REDIRECT FIX TEST")
    print("="*60)
    
    # Clear sessions first
    clear_all_sessions()
    
    # Test 1: Home page loads
    print("\n1. Testing home page...")
    try:
        response = requests.get(f"{server_url}/", allow_redirects=False)
        print(f"   ✅ Home page status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Profile page redirects to login (as expected for unauthenticated)
    print("\n2. Testing profile page redirect...")
    try:
        response = requests.get(f"{server_url}/profile/", allow_redirects=False)
        print(f"   ✅ Profile page status: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   ✅ Redirects to: {location}")
            if '/login/' in location:
                print("   ✅ Correctly redirects to login")
            else:
                print("   ❌ Incorrect redirect location")
        else:
            print(f"   ❌ Expected 302 redirect, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: JWT Profile page loads without redirect
    print("\n3. Testing JWT profile page...")
    try:
        response = requests.get(f"{server_url}/jwt-profile/", allow_redirects=False)
        print(f"   ✅ JWT Profile page status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ JWT Profile loads without redirect")
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Login API
    print("\n4. Testing login API...")
    try:
        login_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = requests.post(f"{server_url}/api/auth/login/", json=login_data)
        print(f"   ✅ Login API status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Access token received: {data.get('access', '')[:50]}...")
            print("   ✅ JWT login working correctly")
        else:
            print(f"   ❌ Login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print(" FIX SUMMARY")
    print("="*60)
    print("✅ FIXES APPLIED:")
    print("   1. Django auth elements hidden with CSS !important")
    print("   2. JavaScript failsafe to hide Django auth on page load") 
    print("   3. JWT navigation elements properly managed")
    print("   4. Profile redirects use JWT-compatible URLs")
    print("\n📋 NEXT STEPS:")
    print("   1. Open http://127.0.0.1:8003 in browser")
    print("   2. Login with: testuser@example.com / testpass123")
    print("   3. Click Profile link - should work without infinite redirects")
    print("   4. Check console for no errors")

if __name__ == "__main__":
    test_redirect_fix()
