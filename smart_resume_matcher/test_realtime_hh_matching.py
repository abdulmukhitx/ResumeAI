#!/usr/bin/env python3
"""
Test script to verify real-time HH API job matching functionality
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
from jobs.realtime_hh_client import EnhancedHHApiClient, RealTimeJobMatcher
from django.test import Client

User = get_user_model()

def test_hh_api_client():
    """Test the enhanced HH API client"""
    print("🔍 Testing Enhanced HH API Client")
    print("=" * 50)
    
    # Create client
    client = EnhancedHHApiClient()
    
    # Test 1: Basic job search
    print("\n1. Testing basic job search...")
    try:
        jobs = client.fetch_jobs_from_both_apis(
            search_query="python developer",
            location="almaty",
            per_page=10
        )
        print(f"✅ Found {len(jobs)} jobs from both APIs")
        
        if jobs:
            print("Sample job:")
            job = jobs[0]
            print(f"   - Title: {job.get('name', 'N/A')}")
            print(f"   - Company: {job.get('employer', {}).get('name', 'N/A')}")
            print(f"   - Location: {job.get('area', {}).get('name', 'N/A')}")
            print(f"   - URL: {job.get('alternate_url', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Basic search failed: {e}")
        return False
    
    # Test 2: Skills-based search
    print("\n2. Testing skills-based search...")
    try:
        jobs = client.search_jobs_for_resume(
            resume_text="Python developer with Django experience",
            skills=["Python", "Django", "React", "JavaScript"],
            location="moscow",
            limit=10
        )
        print(f"✅ Found {len(jobs)} jobs matching skills")
        
    except Exception as e:
        print(f"❌ Skills search failed: {e}")
        return False
    
    return True

def test_realtime_matcher():
    """Test the real-time job matcher"""
    print("\n🔍 Testing Real-Time Job Matcher")
    print("=" * 50)
    
    # Get test user
    try:
        user = User.objects.get(email="testuser@example.com")
        print(f"✅ Test user found: {user.email}")
    except User.DoesNotExist:
        print("❌ Test user not found")
        return False
    
    # Get user resume
    user_resume = Resume.objects.filter(user=user, is_active=True).first()
    if not user_resume:
        print("❌ No active resume found for test user")
        return False
    
    print(f"✅ Resume found: {user_resume.original_filename}")
    
    # Create matcher
    matcher = RealTimeJobMatcher(user=user, resume=user_resume)
    
    # Test 1: Auto-match based on resume
    print("\n1. Testing auto-match based on resume...")
    try:
        jobs = matcher.find_matching_jobs(limit=10)
        print(f"✅ Found {len(jobs)} matching jobs")
        
        if jobs:
            print("Top matches:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"   {i}. {job.get('title', 'N/A')} - {job.get('match_score', 0)}% match")
                print(f"      Skills: {job.get('matching_skills', [])}")
    
    except Exception as e:
        print(f"❌ Auto-match failed: {e}")
        return False
    
    # Test 2: Search with query
    print("\n2. Testing search with query...")
    try:
        jobs = matcher.find_matching_jobs(
            search_query="Python developer",
            location="almaty",
            limit=10
        )
        print(f"✅ Found {len(jobs)} jobs for query 'Python developer'")
        
    except Exception as e:
        print(f"❌ Query search failed: {e}")
        return False
    
    return True

def test_web_interface():
    """Test the web interface with real-time matching"""
    print("\n🔍 Testing Web Interface")
    print("=" * 50)
    
    # Test user credentials
    email = "testuser@example.com"
    password = "newpassword123"
    
    client = Client()
    
    # Login
    login_response = client.post('/api/auth/login/', {
        'email': email,
        'password': password
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token_data = login_response.json()
    token = token_data.get('access')
    print("✅ Login successful")
    
    # Test AI job matches page with auto-search
    print("\n1. Testing AI job matches with auto-search...")
    try:
        response = client.get(
            '/jobs/ai-matches/?auto_search=true',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        
        if response.status_code == 200:
            print("✅ AI job matches page loaded successfully")
            
            # Check if jobs are in response
            content = response.content.decode('utf-8')
            if 'job-card' in content:
                import re
                job_cards = re.findall(r'<div class="job-card"', content)
                print(f"✅ Found {len(job_cards)} job cards in response")
            else:
                print("⚠️  No job cards found in response")
                
        else:
            print(f"❌ AI job matches page failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Real-Time HH API Job Matching Tests")
    print("=" * 60)
    
    success = True
    
    # Test 1: HH API Client
    if not test_hh_api_client():
        success = False
    
    # Test 2: Real-time matcher
    if not test_realtime_matcher():
        success = False
    
    # Test 3: Web interface
    if not test_web_interface():
        success = False
    
    if success:
        print("\n✅ All tests passed! Real-time HH API job matching is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
    
    sys.exit(0 if success else 1)
