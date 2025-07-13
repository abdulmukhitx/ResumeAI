#!/usr/bin/env python3
"""
Test script to verify that the login functionality works end-to-end
"""
import requests
import json

# Test the API endpoint directly first
def test_api_login():
    print("Testing API login endpoint...")
    
    url = "http://127.0.0.1:8000/api/auth/token/"
    data = {
        "email": "a_nurkazy@kbtu.kz",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ API login successful!")
            print(f"Access Token: {token_data.get('access', 'N/A')[:50]}...")
            print(f"Refresh Token: {token_data.get('refresh', 'N/A')[:50]}...")
            return True
        else:
            print("❌ API login failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_home_page_with_token():
    print("\nTesting home page access...")
    
    # First get a token
    token_url = "http://127.0.0.1:8000/api/auth/token/"
    token_data = {
        "email": "a_nurkazy@kbtu.kz",
        "password": "testpass123"
    }
    
    try:
        token_response = requests.post(token_url, json=token_data)
        if token_response.status_code == 200:
            tokens = token_response.json()
            access_token = tokens['access']
            
            # Test home page access
            home_url = "http://127.0.0.1:8000/"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            home_response = requests.get(home_url, headers=headers)
            print(f"Home page status: {home_response.status_code}")
            
            if "dashboard" in home_response.text.lower() or "welcome" in home_response.text.lower():
                print("✅ Home page accessible with token")
                return True
            else:
                print("⚠️ Home page loaded but may not show authenticated content")
                return False
                
    except Exception as e:
        print(f"❌ Error testing home page: {e}")
        return False

if __name__ == "__main__":
    print("=== JWT Authentication Test ===\n")
    
    api_ok = test_api_login()
    home_ok = test_home_page_with_token()
    
    print(f"\n=== Results ===")
    print(f"API Login: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Home Access: {'✅ PASS' if home_ok else '❌ FAIL'}")
    
    if api_ok and home_ok:
        print("\n🎉 Backend authentication is working correctly!")
        print("Now test the frontend login form in the browser.")
    else:
        print("\n❌ There are issues with the backend authentication.")
