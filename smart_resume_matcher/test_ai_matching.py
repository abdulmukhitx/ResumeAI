#!/usr/bin/env python3
"""
Test script for AI Job Matching functionality
"""
import os
import sys
import django
import asyncio
from asgiref.sync import sync_to_async

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from resumes.models import Resume
from jobs.models import Job, JobMatch
from resumes.enhanced_job_matcher import AdvancedJobMatcher, JobMatchingService

async def test_ai_job_matching():
    """Test the AI job matching functionality"""
    print("🧪 Testing AI Job Matching System...")
    
    # Get a test user
    user = await sync_to_async(User.objects.filter(username='testuser@example.com').first)()
    if not user:
        print("❌ Test user not found. Trying another user...")
        user = await sync_to_async(User.objects.first)()
        if not user:
            print("❌ No users found in database")
            return
    
    print(f"✅ Found test user: {user.username}")
    
    # Get user's resume
    resume = await sync_to_async(Resume.objects.filter(user=user, is_active=True).first)()
    if not resume:
        print("❌ No active resume found for test user")
        # Try to get any resume for this user
        resume = await sync_to_async(Resume.objects.filter(user=user).first)()
        if not resume:
            print("❌ No resume found for test user")
            return
    
    print(f"✅ Found resume: {resume.file.name if resume.file else 'No file'}")
    
    # Test basic matcher initialization
    try:
        matcher = AdvancedJobMatcher(user=user, resume=resume)
        print("✅ Advanced job matcher initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing matcher: {e}")
        return
    
    # Test resume analysis
    try:
        print("\n📊 Testing resume analysis...")
        analysis = await matcher.analyze_resume_advanced()
        
        if analysis:
            print("✅ Resume analysis completed")
            print(f"   - Skills categories: {len(analysis.get('skills_with_confidence', {}))}")
            print(f"   - Experience depth: {analysis.get('experience_depth', {}).get('total_years', 0)} years")
            print(f"   - Domain expertise: {len(analysis.get('domain_expertise', {}))}")
        else:
            print("⚠️  Resume analysis returned empty results")
    except Exception as e:
        print(f"❌ Error in resume analysis: {e}")
    
    # Test job matching
    try:
        print("\n🔍 Testing job matching...")
        matches = await matcher.generate_advanced_job_matches(limit=5)
        
        if matches:
            print(f"✅ Found {len(matches)} job matches")
            for i, match in enumerate(matches[:3], 1):
                job = match.get('job')
                score = match.get('match_score', 0)
                confidence = match.get('confidence_level', 'unknown')
                print(f"   {i}. {job.title} - Score: {score:.1f}% - Confidence: {confidence}")
        else:
            print("⚠️  No job matches found")
    except Exception as e:
        print(f"❌ Error in job matching: {e}")
    
    # Test service-level matching
    try:
        print("\n🚀 Testing JobMatchingService...")
        result = await JobMatchingService.match_user_with_jobs(user, resume)
        
        if result.get('success'):
            print("✅ JobMatchingService completed successfully")
            print(f"   - Matches count: {result.get('matches_count', 0)}")
        else:
            print(f"❌ JobMatchingService failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error in JobMatchingService: {e}")
    
    # Test getting existing matches
    try:
        print("\n📋 Testing existing matches retrieval...")
        existing_matches = await JobMatchingService.get_user_matches(user, resume, limit=5)
        
        if existing_matches:
            print(f"✅ Found {len(existing_matches)} existing matches")
            for i, match in enumerate(existing_matches[:3], 1):
                job = match.get('job')
                score = match.get('match_score', 0)
                print(f"   {i}. {job.title} - Score: {score:.1f}%")
        else:
            print("⚠️  No existing matches found")
    except Exception as e:
        print(f"❌ Error retrieving existing matches: {e}")
    
    print("\n🏁 AI Job Matching test completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_job_matching())
