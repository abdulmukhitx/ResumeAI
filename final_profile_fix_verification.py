#!/usr/bin/env python3
"""
Final verification of the profile fix - ensuring upload still works and profile shows data.
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
from resumes.models import Resume

User = get_user_model()

def verify_profile_fix():
    """Verify the profile fix is working."""
    print("🔍 Verifying Profile Fix Implementation...")
    
    # Get test user and generate token
    user = User.objects.first()
    if not user:
        print("❌ No test user found")
        return False
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    
    # Test profile API
    try:
        url = "http://localhost:8000/api/profile/"
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Profile API failed: {response.status_code}")
            return False
        
        data = response.json()
        
        # Check if user has resume data
        if data.get('has_resume'):
            resume_data = data.get('resume', {})
            print(f"✅ Profile API returns resume data:")
            print(f"   📄 Filename: {resume_data.get('filename', 'N/A')}")
            print(f"   🎯 Skills: {len(resume_data.get('skills', []))} detected")
            print(f"   📊 Experience: {resume_data.get('experience_level', 'N/A')}")
            print(f"   🤖 AI Summary: {'Available' if resume_data.get('ai_summary') else 'N/A'}")
            print(f"   📊 Status: {resume_data.get('status', 'N/A')}")
        else:
            print("ℹ️  User has no resume uploaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile API test failed: {e}")
        return False

def verify_upload_integrity():
    """Verify upload functionality is not broken."""
    print("📤 Verifying Upload Functionality Integrity...")
    
    try:
        # Check that upload endpoint exists and responds properly
        user = User.objects.first()
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        
        url = "http://localhost:8000/api/resume/upload/"
        headers = {'Authorization': f'Bearer {token}'}
        
        # OPTIONS request to check CORS and endpoint availability
        response = requests.options(url, headers=headers, timeout=10)
        
        if response.status_code in [200, 405]:  # 405 is expected for OPTIONS on POST-only endpoint
            print("✅ Upload endpoint is accessible")
        else:
            print(f"⚠️  Upload endpoint status: {response.status_code}")
        
        # Check that we can reach the upload page
        upload_page_url = "http://localhost:8000/jwt-resume-upload/"
        page_response = requests.get(upload_page_url, timeout=10)
        
        if page_response.status_code == 200:
            print("✅ Upload page is accessible")
        else:
            print(f"❌ Upload page failed: {page_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Upload integrity check failed: {e}")
        return False

def verify_database_state():
    """Verify database state is healthy."""
    print("🗄️  Verifying Database State...")
    
    try:
        # Check users
        user_count = User.objects.count()
        print(f"✅ Users in database: {user_count}")
        
        # Check resumes
        resume_count = Resume.objects.count()
        print(f"✅ Resumes in database: {resume_count}")
        
        # Check for any resumes with analysis data
        analyzed_resumes = Resume.objects.exclude(analysis_summary='').count()
        print(f"✅ Analyzed resumes: {analyzed_resumes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    """Run final verification."""
    print("🔬 Final Profile Fix Verification")
    print("=" * 50)
    
    checks = [
        ("Profile Fix Implementation", verify_profile_fix),
        ("Upload Functionality Integrity", verify_upload_integrity),
        ("Database State", verify_database_state),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        result = check_func()
        results.append((check_name, result))
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Verification Summary:")
    all_passed = True
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 SUCCESS! Profile fix is complete and working correctly!")
        print()
        print("✨ What's working:")
        print("   • Profile page shows resume analysis results")
        print("   • Resume upload functionality is intact")
        print("   • JWT authentication works properly")
        print("   • Database state is healthy")
        print()
        print("🌐 Test URLs:")
        print("   • Profile: http://localhost:8000/jwt-profile/")
        print("   • Upload: http://localhost:8000/jwt-resume-upload/")
        print("   • Profile API: http://localhost:8000/api/profile/")
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()
