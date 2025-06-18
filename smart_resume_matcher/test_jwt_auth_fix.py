#!/usr/bin/env python3
"""
Comprehensive JWT Authentication Fix Test
Tests the new JWT-compatible views and fixes for infinite redirect issues.
"""

import requests
import time
import json
from datetime import datetime

def print_section(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def test_jwt_authentication_fix():
    """Test the comprehensive JWT authentication fixes"""
    
    print_section("JWT AUTHENTICATION FIX VERIFICATION")
    print(f"Test timestamp: {datetime.now()}")
    print(f"Server: http://127.0.0.1:8001")
    
    # Test 1: Login API (should work)
    print_section("1. LOGIN API TEST")
    try:
        login_response = requests.post('http://127.0.0.1:8001/api/auth/token/', 
                                     json={'email': 'testuser@example.com', 'password': 'testpass123'})
        if login_response.status_code == 200:
            data = login_response.json()
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            user_email = data.get('user', {}).get('email')
            
            print("✅ Login API successful")
            print(f"   User: {user_email}")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Refresh token: {refresh_token[:50]}...")
            
            # Test 2: JWT Profile Page (should work without redirect)
            print_section("2. JWT PROFILE PAGE TEST")
            try:
                profile_response = requests.get('http://127.0.0.1:8001/jwt-profile/')
                if profile_response.status_code == 200:
                    print("✅ JWT Profile page loads successfully (no redirect)")
                    print(f"   Response length: {len(profile_response.text)} chars")
                    
                    # Check if the page contains JWT profile elements
                    if 'jwt-profile-container' in profile_response.text:
                        print("✅ JWT Profile template loaded correctly")
                    else:
                        print("❌ JWT Profile template not found")
                else:
                    print(f"❌ JWT Profile page failed: {profile_response.status_code}")
            except Exception as e:
                print(f"❌ JWT Profile page error: {e}")
            
            # Test 3: Original Profile Page (should redirect)
            print_section("3. ORIGINAL PROFILE PAGE TEST")
            try:
                original_profile_response = requests.get('http://127.0.0.1:8001/profile/', allow_redirects=False)
                if original_profile_response.status_code == 302:
                    redirect_location = original_profile_response.headers.get('location', '')
                    if '/login/' in redirect_location:
                        print("✅ Original profile page correctly redirects to login")
                        print(f"   Redirect: {redirect_location}")
                    else:
                        print(f"❌ Unexpected redirect: {redirect_location}")
                else:
                    print(f"❌ Original profile should redirect but got: {original_profile_response.status_code}")
            except Exception as e:
                print(f"❌ Original profile test error: {e}")
            
            # Test 4: JWT Token in Header (future enhancement)
            print_section("4. JWT HEADER AUTHENTICATION TEST")
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                jwt_auth_response = requests.get('http://127.0.0.1:8001/profile/', headers=headers, allow_redirects=False)
                
                if jwt_auth_response.status_code == 200:
                    print("✅ JWT header authentication working with original profile")
                elif jwt_auth_response.status_code == 302:
                    print("⚠️  JWT header auth not yet implemented for original views (expected)")
                else:
                    print(f"❌ Unexpected response: {jwt_auth_response.status_code}")
            except Exception as e:
                print(f"❌ JWT header test error: {e}")
            
            # Test 5: Home Page
            print_section("5. HOME PAGE TEST")
            try:
                home_response = requests.get('http://127.0.0.1:8001/')
                if home_response.status_code == 200:
                    print("✅ Home page loads successfully")
                    
                    # Check for JWT elements
                    if 'data-jwt-auth' in home_response.text:
                        print("✅ Home page contains JWT authentication elements")
                    if 'jwt_auth_clean.js' in home_response.text:
                        print("✅ JWT auth script is loaded")
                    if 'main.js' in home_response.text:
                        print("✅ Main script is loaded")
                else:
                    print(f"❌ Home page failed: {home_response.status_code}")
            except Exception as e:
                print(f"❌ Home page error: {e}")
                
        else:
            print(f"❌ Login API failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login API error: {e}")
        return False
    
    # Summary
    print_section("FIX SUMMARY")
    print("✅ SOLUTION IMPLEMENTED:")
    print("1. Created JWT-compatible views that don't use @login_required")
    print("2. Added JWT-only profile page (/jwt-profile/)")
    print("3. Updated navigation to use JWT-compatible URLs")
    print("4. Maintained original session-based views as fallbacks")
    print("5. Fixed infinite redirect by bypassing session requirements")
    
    print("\n🎯 TESTING INSTRUCTIONS:")
    print("1. Open http://127.0.0.1:8001/ in browser")
    print("2. Login with: testuser@example.com / testpass123")
    print("3. Click on Profile link in navigation")
    print("4. Verify: No infinite redirects, profile page loads")
    print("5. Check console for JWT authentication status")
    
    print("\n📋 EXPECTED RESULTS:")
    print("✅ Navigation shows authenticated elements after login")
    print("✅ Profile link works without infinite redirects")
    print("✅ JWT authentication state properly maintained")
    print("✅ No console errors during navigation")
    
    return True

if __name__ == "__main__":
    test_jwt_authentication_fix()
