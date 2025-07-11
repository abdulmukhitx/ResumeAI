#!/usr/bin/env python3
"""
Test script to verify AI job matches functionality
"""
import os
import sys
import django
import requests
import json
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import Resume
from jobs.models import Job, JobMatch
from django.test import RequestFactory, Client
from django.urls import reverse

User = get_user_model()

def test_ai_job_matches():
    """Test AI job matches functionality"""
    print("🔍 Testing AI Job Matches Functionality")
    print("=" * 50)
    
    # Test user credentials
    email = "testuser@example.com"
    password = "newpass123"
    
    # 1. Check if test user exists
    try:
        user = User.objects.get(email=email)
        print(f"✅ Test user found: {user.email}")
    except User.DoesNotExist:
        print(f"❌ Test user not found: {email}")
        return False
    
    # 2. Check if user has a resume
    user_resume = Resume.objects.filter(user=user, is_active=True).first()
    if not user_resume:
        print("❌ No active resume found for test user")
        return False
    
    print(f"✅ Resume found: {user_resume.original_filename}")
    
    # 3. Check jobs in database
    total_jobs = Job.objects.filter(is_active=True).count()
    print(f"✅ Total active jobs in database: {total_jobs}")
    
    # 4. Test login and get JWT token
    client = Client()
    login_response = client.post('/api/auth/login/', {
        'email': email,
        'password': password
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token_data = login_response.json()
    token = token_data.get('access')
    if not token:
        print("❌ No access token received")
        return False
    
    print("✅ Login successful, token received")
    
    # 5. Test AI job matches page (GET request)
    print("\n🔍 Testing AI Job Matches Page")
    
    # First, access the page without auto-search
    response = client.get('/jobs/ai-matches/', HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code != 200:
        print(f"❌ AI matches page failed: {response.status_code}")
        return False
    
    print("✅ AI matches page loads successfully")
    
    # 6. Test auto-search functionality
    print("\n🔍 Testing Auto-Search Functionality")
    
    auto_search_response = client.get('/jobs/ai-matches/?auto_search=true', HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if auto_search_response.status_code != 200:
        print(f"❌ Auto-search failed: {auto_search_response.status_code}")
        return False
    
    print("✅ Auto-search completed successfully")
    
    # 7. Check if JobMatch records were created
    job_matches = JobMatch.objects.filter(resume=user_resume)
    print(f"✅ JobMatch records found: {job_matches.count()}")
    
    if job_matches.exists():
        # Show some sample matches
        print("\n📊 Sample Job Matches:")
        for match in job_matches[:5]:
            print(f"   - {match.job.title} ({match.job.company_name}): {match.match_score}% match")
    
    # 8. Test the template context
    print("\n🔍 Testing Template Context")
    
    # Use Django's test client to simulate the view
    from django.test import RequestFactory
    from jobs.views import ai_job_matches_view
    
    factory = RequestFactory()
    request = factory.get('/jobs/ai-matches/?auto_search=true')
    request.user = user
    
    # Add JWT token to request for our decorator
    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    try:
        response = ai_job_matches_view(request)
        if response.status_code == 200:
            print("✅ View executed successfully")
        else:
            print(f"❌ View failed with status: {response.status_code}")
    except Exception as e:
        print(f"❌ View error: {e}")
        return False
    
    print("\n✅ All tests passed! AI Job Matches functionality is working correctly.")
    return True

if __name__ == "__main__":
    success = test_ai_job_matches()
    sys.exit(0 if success else 1)
