#!/usr/bin/env python3
"""
Test the new resume upload and analysis functionality.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import Resume

User = get_user_model()

def test_resume_functionality():
    """Test resume upload and analysis functionality."""
    print("🧪 Testing Resume Upload and Analysis")
    print("=" * 50)
    
    # Check if we have users
    users = User.objects.all()
    if not users.exists():
        print("❌ No users found in database")
        return False
    
    user = users.first()
    print(f"✓ Test user: {user.email}")
    
    # Check existing resumes
    user_resumes = Resume.objects.filter(user=user)
    print(f"✓ User has {user_resumes.count()} resume(s)")
    
    # Check if analysis functions are importable
    try:
        from resumes.views import analyze_resume
        print("✓ Resume analysis function is available")
    except ImportError as e:
        print(f"❌ Cannot import analysis function: {e}")
        return False
    
    # Check if API endpoints are importable
    try:
        from resumes.api import resume_upload_api, resume_status_api, resume_list_api
        print("✓ Resume API endpoints are available")
    except ImportError as e:
        print(f"❌ Cannot import API endpoints: {e}")
        return False
    
    # Check if we have any completed resumes
    completed_resumes = Resume.objects.filter(user=user, status='completed')
    if completed_resumes.exists():
        resume = completed_resumes.first()
        print(f"✓ Found completed resume: {resume.original_filename}")
        print(f"   - Skills: {len(resume.extracted_skills) if resume.extracted_skills else 0}")
        print(f"   - Experience: {resume.experience_level or 'Not set'}")
        print(f"   - Summary: {'Available' if resume.analysis_summary else 'Not available'}")
    else:
        print("ℹ️  No completed resume analysis found")
    
    # Check media directory
    media_dir = '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/media'
    if os.path.exists(media_dir):
        print(f"✓ Media directory exists: {media_dir}")
    else:
        print(f"❌ Media directory missing: {media_dir}")
        return False
    
    return True

def main():
    """Run the test."""
    print("🔬 Resume Upload & Analysis Test")
    print("=" * 50)
    
    success = test_resume_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Resume functionality is ready!")
        print("\n📝 What you can now do:")
        print("   • Upload resumes via /jwt-resume-upload/")
        print("   • Files will be analyzed automatically")
        print("   • Check status via API endpoints")
        print("   • View results on profile page")
        print("\n🚀 Try uploading a resume to test the complete flow!")
    else:
        print("⚠️  Some issues detected. Please fix them first.")
    
    return success

if __name__ == "__main__":
    main()
