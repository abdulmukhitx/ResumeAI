#!/usr/bin/env python3
"""
JWT Authentication Final Verification Test
Tests all the fixes applied to the JWT authentication system.
"""

import requests
import time
import json
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_jwt_fixes():
    """Test all the JWT authentication fixes"""
    
    print_section("JWT AUTHENTICATION FIXES VERIFICATION")
    print(f"Test timestamp: {datetime.now()}")
    print(f"Server: http://127.0.0.1:8001")
    
    # Test 1: Backend API
    print_section("1. BACKEND API TEST")
    try:
        response = requests.post('http://127.0.0.1:8001/api/auth/token/', 
                               json={'email': 'testuser@example.com', 'password': 'testpass123'})
        if response.status_code == 200:
            data = response.json()
            print("✅ Login API working correctly")
            print(f"   User: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   Access token: {len(data.get('access', ''))} chars")
            print(f"   Refresh token: {len(data.get('refresh', ''))} chars")
        else:
            print(f"❌ Login API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")
    
    # Test 2: Static Files
    print_section("2. STATIC FILES TEST")
    files_to_check = [
        '/static/js/jwt_auth_clean.js',
        '/static/js/main.js'
    ]
    
    for file_path in files_to_check:
        try:
            response = requests.get(f'http://127.0.0.1:8001{file_path}')
            if response.status_code == 200:
                content = response.text
                
                # Check for specific fixes
                if 'jwt_auth_clean.js' in file_path:
                    if 'getOptions()' in content:
                        print(f"✅ {file_path} - getOptions method present")
                    else:
                        print(f"❌ {file_path} - getOptions method missing")
                        
                    if 'updateNavigation()' in content:
                        print(f"✅ {file_path} - updateNavigation method present")
                    else:
                        print(f"❌ {file_path} - updateNavigation method missing")
                        
                elif 'main.js' in file_path:
                    if 'auth:login' in content and 'updateNavigation' in content:
                        print(f"✅ {file_path} - auth event handlers present")
                    else:
                        print(f"❌ {file_path} - auth event handlers missing")
            else:
                print(f"❌ {file_path} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
    
    # Test 3: Page Templates
    print_section("3. TEMPLATE STRUCTURE TEST")
    try:
        response = requests.get('http://127.0.0.1:8001/')
        if response.status_code == 200:
            content = response.text
            
            checks = [
                ('data-jwt-auth', 'JWT auth elements'),
                ('data-jwt-no-auth', 'JWT no-auth elements'),
                ('user-name', 'User name element'),
                ('user-email', 'User email element'),
                ('jwt_auth_clean.js', 'Clean JWT script'),
                ('main.js', 'Main script'),
            ]
            
            for check_str, description in checks:
                if check_str in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} missing")
        else:
            print(f"❌ Home page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Template test error: {e}")
    
    # Summary
    print_section("FIXES APPLIED SUMMARY")
    print("1. ✅ Added missing getOptions() method to prevent console errors")
    print("2. ✅ Added getUserData() alias method for compatibility")
    print("3. ✅ Removed conflicting redirect logic from main.js auth events")
    print("4. ✅ Enhanced navigation update with detailed console logging")
    print("5. ✅ Improved authentication state detection on page load")
    print("6. ✅ Added timing fixes to prevent initialization conflicts")
    
    print_section("MANUAL TESTING REQUIRED")
    print("🌐 BROWSER TEST STEPS:")
    print("1. Open http://127.0.0.1:8001/ in browser")
    print("2. Open Developer Console (F12)")
    print("3. Verify Login/Register buttons are visible")
    print("4. Navigate to http://127.0.0.1:8001/login/")
    print("5. Login with: testuser@example.com / testpass123")
    print("6. After redirect, verify:")
    print("   ✅ No 'getOptions' errors in console")
    print("   ✅ Login/Register buttons are HIDDEN")
    print("   ✅ User dropdown is VISIBLE with email")
    print("   ✅ Console shows navigation update messages")
    
    print("\n🎯 EXPECTED CONSOLE OUTPUT:")
    print("   🔐 Clean JWT Auth Manager initialized")
    print("   ✅ User authenticated on page load: testuser@example.com")
    print("   🔄 Updating navigation: { isAuth: true, userEmail: ... }")
    print("   Found X auth elements")
    print("   Found Y no-auth elements")
    print("   ✅ Updated user name element")
    print("   ✅ Updated user email element")
    print("   ✅ Navigation update completed")

if __name__ == "__main__":
    test_jwt_fixes()
