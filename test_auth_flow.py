#!/usr/bin/env python3
"""
Test script to verify the authentication flow is working correctly
"""
import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000"

def generate_random_email():
    """Generate a random email for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_{random_string}@example.com"

def test_registration():
    """Test user registration"""
    print("🔧 Testing Registration...")
    
    email = generate_random_email()
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register/", json=data, timeout=10)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration successful: {result['user']['email']}")
        return email
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_login(email):
    """Test user login"""
    print(f"🔧 Testing Login for {email}...")
    
    data = {
        "email": email,
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/token/", json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful: {result['user']['email']}")
        print(f"Access token: {result['access'][:50]}...")
        print(f"Refresh token: {result['refresh'][:50]}...")
        return result['access']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_protected_endpoint(access_token):
    """Test accessing a protected endpoint"""
    print("🔧 Testing Protected Endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/api/auth/user/", headers=headers, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Protected endpoint access successful: {result['email']}")
        return True
    else:
        print(f"❌ Protected endpoint access failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_existing_user_login():
    """Test login with existing user"""
    print("🔧 Testing Login with Existing User...")
    
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/token/", json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Existing user login successful: {result['user']['email']}")
        return result['access']
    else:
        print(f"❌ Existing user login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def main():
    print("🚀 Starting Authentication Flow Test")
    print("=" * 50)
    
    # Test 1: Registration
    email = test_registration()
    if not email:
        print("❌ Registration test failed, stopping...")
        return
    
    print()
    
    # Test 2: Login with new user
    access_token = test_login(email)
    if not access_token:
        print("❌ Login test failed, stopping...")
        return
    
    print()
    
    # Test 3: Protected endpoint
    test_protected_endpoint(access_token)
    
    print()
    
    # Test 4: Existing user login
    existing_token = test_existing_user_login()
    if existing_token:
        print()
        test_protected_endpoint(existing_token)
    
    print()
    print("🎉 Authentication flow test completed!")

if __name__ == "__main__":
    main()
