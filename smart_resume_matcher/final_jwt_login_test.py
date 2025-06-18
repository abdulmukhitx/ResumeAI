#!/usr/bin/env python3
"""
Final JWT Login Redirect Manual Test Guide
=========================================

This script provides a complete manual test guide for verifying that the 
infinite redirect loop issue has been resolved.
"""

import os
import django
import sys

# Setup Django environment
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
import requests
import json

User = get_user_model()

def create_test_user():
    """Create a test user for login testing"""
    print("🔧 Setting up test user...")
    
    # Create or get test user
    test_email = "test@example.com"
    test_password = "testpass123"
    
    try:
        user = User.objects.get(email=test_email)
        print(f"   ✅ Test user already exists: {test_email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=test_email,
            password=test_password,
            first_name="Test",
            last_name="User"
        )
        print(f"   ✅ Created test user: {test_email}")
    
    # Ensure password is set correctly
    user.set_password(test_password)
    user.save()
    
    return test_email, test_password

def test_jwt_login_api():
    """Test JWT login API endpoint"""
    print("\n🔐 Testing JWT Login API...")
    
    test_email, test_password = create_test_user()
    
    # Test login endpoint
    login_url = "http://localhost:8000/api/auth/token/"
    
    try:
        response = requests.post(login_url, json={
            "email": test_email,
            "password": test_password
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ JWT Login API successful!")
            print(f"   ✅ Received access token: {data['access'][:50]}...")
            print(f"   ✅ Received refresh token: {data['refresh'][:50]}...")
            print(f"   ✅ User data included: {data['user']['email']}")
            return True
        else:
            print(f"   ❌ JWT Login API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ JWT Login API error: {e}")
        return False

def print_manual_test_guide():
    """Print a comprehensive manual test guide"""
    print("\n" + "="*60)
    print("📋 MANUAL JWT LOGIN REDIRECT TEST GUIDE")
    print("="*60)
    
    test_email, test_password = create_test_user()
    
    print(f"""
🎯 TEST SCENARIO 1: Basic Login Redirect
========================================
1. Open: http://localhost:8000/login/
2. Enter credentials:
   Email: {test_email}
   Password: {test_password}
3. Click "Sign In"
4. ✅ EXPECTED: Should redirect to home page (/) after 500ms
5. ❌ FAILURE: If it stays on login page = infinite redirect bug

🎯 TEST SCENARIO 2: Login with Next Parameter
=============================================
1. Open: http://localhost:8000/login/?next=/profile/
2. Enter credentials:
   Email: {test_email}
   Password: {test_password}
3. Click "Sign In"
4. ✅ EXPECTED: Should redirect to /profile/ after 500ms
5. ❌ FAILURE: If it stays on login page = redirect bug

🎯 TEST SCENARIO 3: Already Authenticated
=========================================
1. Log in first using Test Scenario 1
2. Open: http://localhost:8000/login/
3. ✅ EXPECTED: Should immediately redirect to home page
4. ❌ FAILURE: If login form shows = authentication check bug

🎯 TEST SCENARIO 4: Browser Console Check
=========================================
1. Open browser developer tools (F12)
2. Go to Console tab
3. Perform Test Scenario 1
4. ✅ EXPECTED: See "✅ Clean JWT Auth Manager is ready"
5. ✅ EXPECTED: See "🎉 JWT Login successful"
6. ❌ FAILURE: If console errors = JavaScript bug

🎯 TEST SCENARIO 5: Navigation Update
====================================
1. Before login: Check navigation shows "Login" and "Register"
2. Perform Test Scenario 1
3. ✅ EXPECTED: Navigation updates to show user dropdown
4. ✅ EXPECTED: "Login" and "Register" links disappear
5. ❌ FAILURE: If navigation doesn't update = state management bug

🎯 TEST SCENARIO 6: Cross-Tab Sync
==================================
1. Open two browser tabs to the application
2. Log in on Tab 1
3. ✅ EXPECTED: Tab 2 automatically updates navigation
4. Log out on Tab 1
5. ✅ EXPECTED: Tab 2 automatically redirects to login
6. ❌ FAILURE: If tabs don't sync = event propagation bug

🔧 TROUBLESHOOTING TIPS:
========================
• If login fails: Check Django server logs for API errors
• If redirect fails: Check browser console for JavaScript errors
• If authentication persists: Clear browser storage and try again
• If tokens expire: The system should auto-refresh tokens

🚀 SUCCESS CRITERIA:
====================
✅ Login redirects immediately (no infinite loop)
✅ Console shows no JavaScript errors
✅ Navigation updates correctly
✅ Authentication persists across page refreshes
✅ Cross-tab synchronization works
✅ Logout clears authentication properly

""")

def verify_django_setup():
    """Verify Django is properly configured"""
    print("🔧 Verifying Django setup...")
    
    try:
        # Check database
        user_count = User.objects.count()
        print(f"   ✅ Database accessible, {user_count} users found")
        
        # Check JWT settings
        from django.conf import settings
        if hasattr(settings, 'SIMPLE_JWT'):
            print("   ✅ JWT settings configured")
        else:
            print("   ❌ JWT settings missing")
            
        return True
    except Exception as e:
        print(f"   ❌ Django setup error: {e}")
        return False

def main():
    """Run the complete verification"""
    print("🎯 JWT LOGIN REDIRECT FIX - FINAL VERIFICATION")
    print("=" * 50)
    
    # Verify setup
    if not verify_django_setup():
        print("❌ Django setup failed - please check configuration")
        return
    
    # Test API
    if not test_jwt_login_api():
        print("❌ JWT API test failed - please check server")
        return
    
    # Print manual test guide
    print_manual_test_guide()
    
    print("="*60)
    print("🎉 VERIFICATION COMPLETE!")
    print("="*60)
    print("""
✅ JWT authentication system is ready for testing
✅ Test user created and API verified
✅ Manual test guide provided above

🚀 Next steps:
1. Follow the manual test guide above
2. Confirm all test scenarios pass
3. The infinite redirect loop should be completely resolved!

📍 The Django server should be running at: http://localhost:8000
""")

if __name__ == "__main__":
    main()
