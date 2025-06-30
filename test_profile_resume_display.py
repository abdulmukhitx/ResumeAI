#!/usr/bin/env python3
"""
Test Profile API to verify resume data is available
"""
import os
import sys
import requests

# Test the profile API endpoint
def test_profile_api():
    print("=== Testing Profile API ===")
    
    # First login to get a token
    login_data = {
        'email': 'testuser_3293@example.com',  # Using a test user that we know works
        'password': 'testpass123'
    }
    
    try:
        # Login
        response = requests.post('http://localhost:8001/api/auth/login/', json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
        
        token_data = response.json()
        token = token_data.get('access')
        print(f"✅ Login successful, got token")
        
        # Test profile API
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:8001/api/profile/', headers=headers)
        
        print(f"Profile API status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile API working!")
            print(f"User: {data.get('user', {}).get('email')}")
            
            resume = data.get('resume')
            if resume:
                print(f"✅ Resume found: {resume.get('original_filename')}")
                print(f"   Status: {resume.get('status')}")
                print(f"   Skills: {len(resume.get('extracted_skills', []))} skills")
                print(f"   Experience: {resume.get('experience_level')}")
            else:
                print("❌ No resume data found")
                
            apps = data.get('job_applications', [])
            print(f"Job applications: {len(apps)}")
            
        else:
            print(f"❌ Profile API failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

def check_database_resumes():
    """Check what resumes exist in database"""
    sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    import django
    django.setup()
    
    from accounts.models import User
    from resumes.models import Resume
    
    print("\n=== Database Resume Check ===")
    
    # Check the main user
    try:
        user = User.objects.get(email='a_nurkazy@kbtu.kz')
        print(f"✅ Found user: {user.email}")
        
        resumes = Resume.objects.filter(user=user)
        print(f"Resumes for this user: {resumes.count()}")
        
        for resume in resumes:
            print(f"  - ID: {resume.id}")
            print(f"    File: {resume.original_filename}")
            print(f"    Status: {resume.status}")
            print(f"    Active: {resume.is_active}")
            print(f"    Skills: {len(resume.extracted_skills or [])}")
            print(f"    Created: {resume.created_at}")
            print("    ---")
            
    except User.DoesNotExist:
        print("❌ User not found")
        
    # Check all resumes
    all_resumes = Resume.objects.all()
    print(f"\nTotal resumes in database: {all_resumes.count()}")
    for resume in all_resumes:
        print(f"  Resume {resume.id}: {resume.user.email} - {resume.original_filename} ({resume.status})")

if __name__ == '__main__':
    print("Profile Resume Display Fix Test")
    print("===============================")
    
    check_database_resumes()
    test_profile_api()
    
    print("\n🎯 If profile API shows resume data, the frontend should now display it!")
    print("Visit: http://localhost:8001/jwt-profile/ to test")
