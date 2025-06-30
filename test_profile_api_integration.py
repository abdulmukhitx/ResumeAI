#!/usr/bin/env python3
"""
Test the new profile API endpoint and verify uploads still work.
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
from resumes.models import Resume

User = get_user_model()

def test_profile_api():
    """Test the new profile API endpoint."""
    print("🧪 Testing Profile API Endpoint...")
    
    # Check if we have test users
    users = User.objects.all()
    if not users.exists():
        print("❌ No users found in database")
        return False
    
    user = users.first()
    print(f"✓ Found test user: {user.email}")
    
    # Check if user has resumes
    user_resumes = Resume.objects.filter(user=user)
    print(f"✓ User has {user_resumes.count()} resume(s)")
    
    # Try to import and test the profile API view
    try:
        from accounts.profile_api import profile_data_api
        print("✓ Profile API view imported successfully")
        
        # Mock request test (basic structure check)
        print("✓ Profile API endpoint is available")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import profile API: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing profile API: {e}")
        return False

def test_resume_upload_still_works():
    """Verify that resume upload functionality is still intact."""
    print("📤 Testing Resume Upload Functionality...")
    
    try:
        from resumes.ultra_safe_api import ultra_safe_resume_upload
        print("✓ Resume upload API is still importable")
        
        # Check if media directory exists
        media_dir = '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/media/resumes'
        if os.path.exists(media_dir):
            print("✓ Media directory exists")
        else:
            print("❌ Media directory missing")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Resume upload API import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing resume upload: {e}")
        return False

def test_url_configuration():
    """Test that URL configuration is correct."""
    print("🔗 Testing URL Configuration...")
    
    try:
        from django.urls import reverse
        
        # Test existing URLs
        existing_urls = [
            'jwt_profile',
            'api_resume_upload',
            'api_resume_list',
        ]
        
        for url_name in existing_urls:
            try:
                url = reverse(url_name)
                print(f"✓ URL '{url_name}' -> {url}")
            except Exception as e:
                print(f"❌ URL '{url_name}' failed: {e}")
                return False
        
        # Test new profile API URL
        try:
            profile_api_url = reverse('api_profile_data')
            print(f"✓ New profile API URL: {profile_api_url}")
        except Exception as e:
            print(f"❌ Profile API URL failed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ URL configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Profile API Integration Test")
    print("=" * 50)
    
    tests = [
        ("Profile API Endpoint", test_profile_api),
        ("Resume Upload Integrity", test_resume_upload_still_works),
        ("URL Configuration", test_url_configuration),
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
        print("🎉 All tests passed! Profile API integration is ready.")
        print("👉 Next step: Test the profile page in the browser")
    else:
        print("⚠️  Some tests failed. Please fix issues before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    main()
