#!/usr/bin/env python3
"""
Manual Login Test: Check Authentication State and Navigation Update
This script helps verify that after manual login, the navigation updates correctly.
"""

import time
import requests
import json
from datetime import datetime

def test_manual_login_verification():
    """
    This function guides manual testing of the login and navigation update process.
    """
    print("="*70)
    print("MANUAL LOGIN VERIFICATION TEST")
    print("="*70)
    print(f"Test started at: {datetime.now()}")
    print()
    
    print("📋 MANUAL TEST STEPS:")
    print("1. Open http://127.0.0.1:8001/ in browser")
    print("2. Check that Login/Register buttons are visible in navigation")
    print("3. Open Developer Console (F12)")
    print("4. Go to http://127.0.0.1:8001/login/")
    print("5. Login with: testuser@example.com / testpass123")
    print("6. Watch console output for navigation updates")
    print("7. After redirect to home page, verify:")
    print("   - Login/Register buttons are HIDDEN")
    print("   - User dropdown with name/email is VISIBLE")
    print("   - Console shows authentication status")
    print()
    
    print("🔍 WHAT TO LOOK FOR IN CONSOLE:")
    print("✅ '🔐 Clean JWT Auth Manager initialized'")
    print("✅ '✅ User authenticated on page load: testuser@example.com'")
    print("✅ '🔄 Updating navigation: { isAuth: true, userEmail: ... }'")
    print("✅ 'Found X auth elements' and 'Found Y no-auth elements'")
    print("✅ '✅ Updated user name element'")
    print("✅ '✅ Updated user email element'")
    print("✅ '✅ Navigation update completed'")
    print()
    
    print("❌ ERRORS TO WATCH FOR:")
    print("❌ 'window.authManager.getOptions is not a function'")
    print("❌ 'Auth manager not found!'")
    print("❌ 'Found 0 auth elements' (should be > 0)")
    print("❌ Login/Register buttons still visible after login")
    print()
    
    # Test the API endpoint to ensure backend is working
    print("🧪 TESTING BACKEND API:")
    try:
        response = requests.post('http://127.0.0.1:8001/api/auth/token/', 
                               json={'email': 'testuser@example.com', 'password': 'testpass123'})
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API working - Login endpoint returns tokens")
            print(f"   Access token length: {len(data.get('access', ''))}")
            print(f"   User email: {data.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"❌ Backend API failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Backend API error: {e}")
    
    print()
    print("📊 EXPECTED RESULT:")
    print("After successful login:")
    print("1. Navigation should show authenticated state (user dropdown visible)")
    print("2. Login/Register buttons should be hidden")
    print("3. Console should show successful navigation update")
    print("4. No 'getOptions' errors in console")
    print()
    
    input("Press Enter after completing the manual test...")
    
    print("\n🎯 If the test passed:")
    print("✅ Authentication system is working correctly")
    print("✅ Navigation updates are functioning")
    print("✅ JWT tokens are being stored and retrieved properly")
    
    print("\n❌ If the test failed:")
    print("Check the console errors and compare with expected output above")
    print("Common issues:")
    print("- Navigation elements not updating: Check data-jwt-auth attributes")
    print("- getOptions error: Should be fixed with recent updates")
    print("- User info not showing: Check user data storage/retrieval")

if __name__ == "__main__":
    test_manual_login_verification()
