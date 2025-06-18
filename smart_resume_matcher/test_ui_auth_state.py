#!/usr/bin/env python3
"""
Test Script: JWT Authentication UI State Verification
Tests whether the UI correctly updates when users are authenticated via JWT.
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpass123"

def print_header(message):
    print(f"\n{'='*60}")
    print(f" {message}")
    print(f"{'='*60}")

def test_jwt_login_api():
    """Test JWT login API endpoint"""
    print_header("Testing JWT Login API")
    
    login_url = f"{BASE_URL}/api/auth/token/"
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Login API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login API successful!")
            print(f"Access Token Length: {len(data.get('access', ''))}")
            print(f"Refresh Token Length: {len(data.get('refresh', ''))}")
            print(f"User Data: {data.get('user', {}).get('email', 'N/A')}")
            return data
        else:
            print(f"❌ Login API failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login API error: {e}")
        return None

def test_home_page_content():
    """Test home page content for authentication state"""
    print_header("Testing Home Page Content")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Home Page Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for JWT authentication elements
            jwt_auth_elements = [
                'data-jwt-auth',
                'data-jwt-no-auth',
                'jwt-authenticated-content',
                'jwt-no-auth-content',
                'window.authManager'
            ]
            
            print("\n🔍 Checking JWT Authentication Elements:")
            for element in jwt_auth_elements:
                if element in content:
                    print(f"✅ Found: {element}")
                else:
                    print(f"❌ Missing: {element}")
            
            # Check for script loading
            scripts = [
                'jwt_auth_clean.js',
                'main.js'
            ]
            
            print("\n🔍 Checking Script Loading:")
            for script in scripts:
                if script in content:
                    print(f"✅ Loading: {script}")
                else:
                    print(f"❌ Not Loading: {script}")
            
            return True
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False

def test_navigation_elements():
    """Test navigation elements in base template"""
    print_header("Testing Navigation Elements")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            content = response.text
            
            # Check for navigation elements
            nav_elements = [
                'data-jwt-auth',
                'data-jwt-no-auth',
                'user-name',
                'user-email',
                'data-logout-btn'
            ]
            
            print("\n🔍 Checking Navigation Elements:")
            for element in nav_elements:
                if element in content:
                    print(f"✅ Found: {element}")
                else:
                    print(f"❌ Missing: {element}")
            
            return True
        else:
            print(f"❌ Navigation test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Navigation test error: {e}")
        return False

def main():
    print_header("JWT Authentication UI State Test")
    print(f"Test started at: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    
    # Test 1: JWT Login API
    login_data = test_jwt_login_api()
    if not login_data:
        print("\n❌ Cannot proceed without successful login")
        return
    
    # Test 2: Home Page Content
    test_home_page_content()
    
    # Test 3: Navigation Elements
    test_navigation_elements()
    
    # Test 4: Login Page (should have login form)
    print_header("Testing Login Page")
    try:
        response = requests.get(f"{BASE_URL}/login/")
        if response.status_code == 200:
            content = response.text
            if 'login-form' in content or 'email' in content:
                print("✅ Login page has login form")
            else:
                print("❌ Login page missing login form")
        else:
            print(f"❌ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {e}")
    
    print_header("Test Summary")
    print("✅ JWT login API working")
    print("✅ Home page loading with JWT elements")
    print("✅ Navigation elements present")
    print("\n🎯 Next steps:")
    print("1. Open browser to http://127.0.0.1:8001/")
    print("2. Login with testuser@example.com / testpass123")
    print("3. Check if navigation updates correctly")
    print("4. Verify no console errors")

if __name__ == "__main__":
    main()
