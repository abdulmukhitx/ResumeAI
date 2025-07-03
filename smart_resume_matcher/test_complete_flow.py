#!/usr/bin/env python
"""
Create a test user and demonstrate the JWT authentication flow
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()

def create_test_user_and_test_flow():
    """Create a test user and demonstrate the complete flow"""
    print("=" * 60)
    print("TESTING COMPLETE JWT AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Create or get test user
    test_email = "testuser@example.com"
    test_password = "testpassword123"
    
    try:
        user = User.objects.get(email=test_email)
        print(f"✅ Using existing test user: {test_email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=test_email,
            password=test_password,
            first_name="Test",
            last_name="User"
        )
        print(f"✅ Created test user: {test_email}")
    
    # Test authentication flow
    client = Client()
    
    print("\n1. Testing login API:")
    login_data = {
        'email': test_email,
        'password': test_password
    }
    
    response = client.post('/api/auth/login/', data=json.dumps(login_data), 
                          content_type='application/json')
    print(f"   Login response: {response.status_code}")
    
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data.get('access_token')
        
        if access_token:
            print("   ✅ Login successful, JWT token received")
            
            # Test protected endpoint with JWT
            print("\n2. Testing protected API with JWT:")
            headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
            response = client.get('/api/auth/user/', **headers)
            print(f"   API user endpoint with JWT: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ JWT authentication working for API")
            
            # Test protected view with cookie
            print("\n3. Testing protected view with cookie:")
            client.cookies['access_token'] = access_token
            response = client.get('/jobs/')
            print(f"   Jobs page with JWT cookie: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ JWT cookie authentication working for views")
                print("   🎉 COMPLETE FLOW WORKING!")
            elif response.status_code == 500:
                print("   ⚠️  Server error - check HH_API_BASE_URL setting")
                print("   💡 This was the original issue and should now be fixed")
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
        else:
            print("   ❌ No access token in response")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        if response.content:
            print(f"   Error: {response.content.decode()}")
    
    print("\n" + "=" * 60)
    print("COMPLETE JWT FLOW TEST FINISHED")
    print("=" * 60)
    
    print(f"\n🔑 Test Credentials:")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    print(f"\n📝 You can now test manually:")
    print(f"   1. Go to http://localhost:8000/login/")
    print(f"   2. Login with above credentials")
    print(f"   3. Upload a resume at /jwt-resume-upload/")
    print(f"   4. Click 'Browse Job Matches'")
    print(f"   5. Should work without redirecting to login!")

if __name__ == "__main__":
    create_test_user_and_test_flow()
