#!/usr/bin/env python3
"""
Verify the JWT login fix is working end-to-end
"""
import requests
import json

def test_login_flow():
    print("=== Testing Login Fix ===\n")
    
    print("1. Testing fresh login via API...")
    response = requests.post("http://127.0.0.1:8000/api/auth/token/", json={
        "email": "a_nurkazy@kbtu.kz",
        "password": "testpass123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API login successful")
        print(f"   User: {data['user']['email']}")
        print(f"   Name: {data['user']['first_name']} {data['user']['last_name']}")
        
        # Check tokens
        access_token = data['access']
        refresh_token = data['refresh']
        user_data = data['user']
        
        print(f"\n2. Tokens received:")
        print(f"   Access: {access_token[:50]}...")
        print(f"   Refresh: {refresh_token[:50]}...")
        
        print(f"\n3. Testing authenticated home page access...")
        home_response = requests.get("http://127.0.0.1:8000/", headers={
            'Authorization': f'Bearer {access_token}'
        })
        
        if home_response.status_code == 200:
            print("✅ Home page accessible with token")
            
            # Check for navigation elements
            content = home_response.text
            if 'data-jwt-auth' in content and 'data-jwt-no-auth' in content:
                print("✅ Navigation elements present in home page")
            else:
                print("⚠️ Navigation elements not found in home page")
                
            return True
        else:
            print(f"❌ Home page access failed: {home_response.status_code}")
            return False
            
    else:
        print(f"❌ API login failed: {response.status_code}")
        return False

def instructions():
    print("\n=== Manual Testing Instructions ===\n")
    print("Now test the browser flow:")
    print("1. Open: http://127.0.0.1:8000/login/")
    print("2. Enter credentials:")
    print("   Email: a_nurkazy@kbtu.kz")
    print("   Password: testpass123")
    print("3. Click 'Sign In'")
    print("4. Should see:")
    print("   - 'Login successful! Redirecting...'")
    print("   - Redirect to home page")
    print("   - Navigation shows user dropdown (not Login/Register)")
    print("   - User name 'Abdulmukhit' visible in navigation")
    print("\n🔍 Check browser console for debug output!")

if __name__ == "__main__":
    success = test_login_flow()
    
    if success:
        print("\n🎉 Backend authentication is working!")
        instructions()
    else:
        print("\n❌ Backend authentication has issues!")
