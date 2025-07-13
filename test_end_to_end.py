#!/usr/bin/env python3
"""
End-to-end login test script
"""
import requests
import time

def test_end_to_end_login():
    print("=== End-to-End Login Test ===\n")
    
    # Step 1: Clear any existing cookies/session
    session = requests.Session()
    
    # Step 2: Login and get tokens
    print("1. Testing API login...")
    login_url = "http://127.0.0.1:8000/api/auth/token/"
    login_data = {
        "email": "a_nurkazy@kbtu.kz",
        "password": "testpass123"
    }
    
    try:
        response = session.post(login_url, json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens['access']
            print("✅ Login successful")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   User: {tokens['user']['email']}")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 3: Test home page access with token
    print("\n2. Testing home page access with token...")
    home_url = "http://127.0.0.1:8000/"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        home_response = session.get(home_url, headers=headers)
        print(f"   Home page status: {home_response.status_code}")
        
        # Check if the page contains authenticated content indicators
        home_content = home_response.text.lower()
        auth_indicators = ['dashboard', 'logout', 'profile', 'welcome back']
        found_indicators = [ind for ind in auth_indicators if ind in home_content]
        
        if found_indicators:
            print(f"✅ Found auth indicators: {found_indicators}")
        else:
            print("⚠️ No obvious auth indicators found in home page")
            
        return True
        
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False

def test_token_storage_simulation():
    print("\n=== Token Storage Simulation ===\n")
    
    # Simulate what the frontend should do
    print("3. Simulating frontend token storage...")
    
    # Get tokens
    login_url = "http://127.0.0.1:8000/api/auth/token/"
    login_data = {
        "email": "a_nurkazy@kbtu.kz", 
        "password": "testpass123"
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        
        print("✅ Tokens received from API:")
        print(f"   Access: {tokens['access'][:50]}...")
        print(f"   Refresh: {tokens['refresh'][:50]}...")
        print(f"   User ID: {tokens['user']['id']}")
        print(f"   User Email: {tokens['user']['email']}")
        
        # This is what the frontend JS should store
        print("\n📝 Frontend should store:")
        print(f"   localStorage.setItem('smart_resume_access_token', '{tokens['access'][:30]}...');")
        print(f"   localStorage.setItem('smart_resume_refresh_token', '{tokens['refresh'][:30]}...');")
        print(f"   localStorage.setItem('smart_resume_user_data', JSON.stringify(user));")
        
        return True
    else:
        print("❌ Could not get tokens for simulation")
        return False

if __name__ == "__main__":
    api_ok = test_end_to_end_login()
    storage_ok = test_token_storage_simulation()
    
    print(f"\n=== Final Results ===")
    print(f"API Login & Home Access: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Token Storage Simulation: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    
    if api_ok and storage_ok:
        print("\n🎉 Backend is ready! Issue is likely in frontend token storage/navigation update.")
        print("\n🔧 Next steps:")
        print("1. Test the login form in browser")
        print("2. Check browser console for errors")
        print("3. Verify tokens are stored in localStorage")
        print("4. Check if navigation.updateNavigation() is called")
    else:
        print("\n❌ Backend issues detected!")
        