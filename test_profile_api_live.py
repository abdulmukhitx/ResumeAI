#!/usr/bin/env python3
"""
Comprehensive test of the profile API with a real JWT token.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to the Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_jwt_token():
    """Get a valid JWT token for testing."""
    try:
        user = User.objects.first()
        if not user:
            print("❌ No user found for JWT token generation")
            return None
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"✓ Generated JWT token for user: {user.email}")
        return access_token
    except Exception as e:
        print(f"❌ Failed to generate JWT token: {e}")
        return None

def test_profile_api_with_auth():
    """Test the profile API with proper authentication."""
    print("🔐 Testing Profile API with Authentication...")
    
    # Get JWT token
    token = get_jwt_token()
    if not token:
        return False
    
    try:
        # Test the API endpoint
        url = "http://localhost:8000/api/profile/"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Profile API response received")
            
            # Check response structure
            required_keys = ['authenticated', 'user', 'resume', 'applications', 'has_resume']
            for key in required_keys:
                if key in data:
                    print(f"✓ Response contains '{key}'")
                else:
                    print(f"❌ Response missing '{key}'")
                    return False
            
            # Print some details
            if data.get('has_resume'):
                print(f"✓ User has resume: {data['resume']['filename']}")
                if data['resume'].get('skills'):
                    print(f"✓ Resume has skills: {', '.join(data['resume']['skills'][:3])}...")
                if data['resume'].get('ai_summary'):
                    print(f"✓ Resume has AI summary: {data['resume']['ai_summary'][:50]}...")
            else:
                print("ℹ️  User has no resume")
            
            print(f"✓ User has {len(data.get('applications', []))} job applications")
            
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error testing profile API: {e}")
        return False

def test_resume_upload_api():
    """Test that resume upload API is still working."""
    print("📤 Testing Resume Upload API Status...")
    
    token = get_jwt_token()
    if not token:
        return False
    
    try:
        # Just check the endpoint is available (don't actually upload)
        url = "http://localhost:8000/api/resume/upload/"
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        # Make a GET request (which should return 405 Method Not Allowed, but shows endpoint exists)
        response = requests.get(url, headers=headers, timeout=10)
        
        # Should get 405 (Method Not Allowed) since it's POST only, but endpoint exists
        if response.status_code == 405:
            print("✓ Resume upload endpoint exists and requires POST")
            return True
        elif response.status_code == 401:
            print("❌ Resume upload endpoint returns 401 (auth issue)")
            return False
        else:
            print(f"ℹ️  Resume upload endpoint returned {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for upload test")
        return False
    except Exception as e:
        print(f"❌ Error testing upload API: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("🧪 Comprehensive Profile API Test")
    print("=" * 50)
    
    tests = [
        ("Profile API with Authentication", test_profile_api_with_auth),
        ("Resume Upload API Status", test_resume_upload_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    all_passed = True
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! Profile API is working correctly.")
        print("👉 You can now test the profile page at: http://localhost:8000/jwt-profile/")
    else:
        print("⚠️  Some tests failed. Check the server and try again.")
    
    return all_passed

if __name__ == "__main__":
    main()
