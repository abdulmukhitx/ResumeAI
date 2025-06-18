#!/usr/bin/env python3
"""
Debug the infinite redirect and authentication issues
"""

import requests
import json
from datetime import datetime

def debug_authentication_issues():
    print("=" * 70)
    print("DEBUGGING AUTHENTICATION ISSUES")
    print("=" * 70)
    print(f"Timestamp: {datetime.now()}")
    
    # Test 1: Check if we can access protected pages
    print("\n1. TESTING PROTECTED PAGE ACCESS")
    try:
        # Try to access profile page
        response = requests.get('http://127.0.0.1:8001/profile/', allow_redirects=False)
        print(f"Profile page status: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirect location: {response.headers.get('location', 'No location header')}")
        elif response.status_code == 200:
            print("Profile page accessible (this might be wrong if user not logged in)")
    except Exception as e:
        print(f"Error accessing profile: {e}")
    
    # Test 2: Check login API
    print("\n2. TESTING LOGIN API")
    try:
        login_response = requests.post('http://127.0.0.1:8001/api/auth/token/', 
                                     json={'email': 'testuser@example.com', 'password': 'testpass123'})
        print(f"Login API status: {login_response.status_code}")
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"✅ Login successful - User: {data.get('user', {}).get('email', 'N/A')}")
            access_token = data.get('access')
            
            # Test 3: Try accessing profile with JWT token
            print("\n3. TESTING PROFILE ACCESS WITH JWT")
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get('http://127.0.0.1:8001/profile/', 
                                          headers=headers, allow_redirects=False)
            print(f"Profile with JWT status: {profile_response.status_code}")
            if profile_response.status_code == 302:
                print(f"Still redirecting to: {profile_response.headers.get('location', 'No location')}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    except Exception as e:
        print(f"Error with login API: {e}")
    
    # Test 4: Check home page for authentication elements
    print("\n4. CHECKING HOME PAGE AUTHENTICATION ELEMENTS")
    try:
        home_response = requests.get('http://127.0.0.1:8001/')
        if home_response.status_code == 200:
            content = home_response.text
            
            # Count JWT elements
            jwt_auth_count = content.count('data-jwt-auth')
            jwt_no_auth_count = content.count('data-jwt-no-auth')
            
            print(f"JWT auth elements: {jwt_auth_count}")
            print(f"JWT no-auth elements: {jwt_no_auth_count}")
            
            # Check if scripts are loaded
            if 'jwt_auth_clean.js' in content:
                print("✅ JWT auth script is included")
            else:
                print("❌ JWT auth script missing")
                
            if 'main.js' in content:
                print("✅ Main script is included")
            else:
                print("❌ Main script missing")
    except Exception as e:
        print(f"Error checking home page: {e}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS:")
    print("- If profile redirects even with JWT token: Backend not recognizing JWT")
    print("- If JWT elements hidden: Frontend authentication state not updating")
    print("- If scripts missing: JavaScript not loading properly")
    print("=" * 70)

if __name__ == "__main__":
    debug_authentication_issues()
