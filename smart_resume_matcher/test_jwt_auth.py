#!/usr/bin/env python3
"""
Test JWT Authentication to debug login issues
"""
import requests
import json
import sys

def test_jwt_login():
    """Test JWT login with existing user"""
    base_url = "http://localhost:8000"
    
    # Test users from database
    test_users = [
        {"email": "a_nurkazy@kbtu.kz", "password": "testpass123"},
        {"email": "jwt_test@example.com", "password": "testpass123"},
        {"email": "abu@gmail.com", "password": "testpass123"},
    ]
    
    for user in test_users:
        print(f"\n🔐 Testing login for: {user['email']}")
        
        try:
            # Test login endpoint
            response = requests.post(
                f"{base_url}/api/auth/token/",
                headers={"Content-Type": "application/json"},
                data=json.dumps(user),
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login successful!")
                print(f"Access Token: {data['access'][:50]}...")
                print(f"User Data: {json.dumps(data.get('user', {}), indent=2)}")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def test_token_verify():
    """Test token verification endpoint"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing token verification endpoint...")
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/token/verify/",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"token": "fake_token"}),
            timeout=10
        )
        
        print(f"Token verify endpoint status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Token verify test error: {e}")

if __name__ == "__main__":
    print("🚀 JWT Authentication Test")
    print("=" * 40)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Server is running (Status: {response.status_code})")
    except:
        print("❌ Server is not running on localhost:8000")
        print("Please start the server with: python manage.py runserver")
        sys.exit(1)
    
    # Run tests
    test_token_verify()
    test_jwt_login()
