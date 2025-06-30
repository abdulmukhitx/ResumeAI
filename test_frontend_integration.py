#!/usr/bin/env python
"""
Test Enhanced AI Job Matching Frontend Integration
Tests the complete integration from enhanced analyzer to frontend display
"""

import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.models import Resume
from jobs.models import Job, JobMatch
from resumes.enhanced_analyzer import EnhancedAIAnalyzer
from resumes.enhanced_job_matcher import EnhancedJobMatcher

def test_frontend_integration():
    """Test that enhanced AI results are properly displayed in frontend"""
    print("=== Testing Enhanced AI Frontend Integration ===\n")
    
    # Get or create test user
    User = get_user_model()
    test_user, created = User.objects.get_or_create(
        username='test_enhanced_user',
        defaults={
            'email': 'test_enhanced@example.com',
            'password': 'testpass123'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Using existing test user: {test_user.username}")
    
    # Create test resume with enhanced analysis
    resume_content = """
    Senior Python Developer
    
    SKILLS:
    - Python (5+ years)
    - Django, Flask
    - PostgreSQL, MongoDB
    - AWS, Docker, Kubernetes
    - React.js, JavaScript
    - Machine Learning (scikit-learn, TensorFlow)
    - Git, CI/CD
    
    EXPERIENCE:
    Senior Software Engineer at TechCorp (2020-2023)
    - Built scalable web applications using Django and React
    - Implemented microservices architecture with Docker
    - Led team of 5 developers on ML projects
    
    Python Developer at StartupAI (2018-2020)
    - Developed machine learning models for recommendation systems
    - Optimized database queries reducing response time by 60%
    """
    
    # Check if resume exists, if not create one
    resume = Resume.objects.filter(user=test_user, is_active=True).first()
    
    if not resume:
        resume = Resume.objects.create(
            user=test_user,
            filename="test_enhanced_resume.txt",
            content=resume_content,
            is_active=True
        )
        print(f"✓ Created test resume: {resume.filename}")
    else:
        # Update existing resume with fresh content
        resume.content = resume_content
        resume.save()
        print(f"✓ Updated existing resume: {resume.filename}")
    
    # Run enhanced analysis
    print("\n--- Running Enhanced Analysis ---")
    analyzer = EnhancedAIAnalyzer()
    analysis_result = analyzer.analyze_resume(resume.content)
    
    print(f"✓ Extracted {len(analysis_result.get('technical_skills', []))} technical skills")
    print(f"✓ Found {len(analysis_result.get('job_titles', []))} job titles")
    print(f"✓ Experience level: {analysis_result.get('experience_level', 'Unknown')}")
    
    # Update resume with enhanced analysis
    resume.extracted_skills = analysis_result.get('all_skills', [])
    resume.job_titles = analysis_result.get('job_titles', [])
    resume.experience_level = analysis_result.get('experience_level', 'mid')
    resume.analysis_data = analysis_result
    resume.save()
    
    print("✓ Updated resume with enhanced analysis data")
    
    # Test enhanced job matching
    print("\n--- Testing Enhanced Job Matching ---")
    enhanced_matcher = EnhancedJobMatcher(user=test_user, resume=resume)
    
    # Generate job matches
    enhanced_matches = enhanced_matcher.generate_job_matches(limit=5)
    
    if enhanced_matches:
        print(f"✓ Generated {len(enhanced_matches)} enhanced job matches")
        
        # Show sample match details
        for i, match in enumerate(enhanced_matches[:2], 1):
            job = match.get('job')
            if job:
                print(f"\nSample Match {i}:")
                print(f"  Job: {job.title} at {job.company_name}")
                print(f"  Match Score: {match.get('match_score', 0):.1f}%")
                print(f"  Matching Skills: {match.get('matching_skills', [])[:5]}")
                print(f"  Missing Skills: {match.get('missing_skills', [])[:3]}")
    else:
        print("⚠ No enhanced matches generated")
    
    # Test frontend views with Django test client
    print("\n--- Testing Frontend Views ---")
    client = Client()
    
    # Login the user
    login_success = client.login(username='test_enhanced_user', password='testpass123')
    if login_success:
        print("✓ Successfully logged in test user")
    else:
        print("✗ Failed to login test user")
        return
    
    # Test AI job matches view
    response = client.get('/jobs/ai-matches/?auto_search=true')
    
    if response.status_code == 200:
        print("✓ AI job matches view loaded successfully")
        
        # Check if enhanced data is in context
        context = response.context
        if context:
            jobs = context.get('jobs', [])
            job_matches_dict = context.get('job_matches_dict', {})
            
            print(f"✓ Found {len(jobs)} jobs in context")
            print(f"✓ Found {len(job_matches_dict)} job matches in context")
            
            # Check if matches have enhanced data
            if job_matches_dict:
                sample_match = list(job_matches_dict.values())[0]
                if hasattr(sample_match, 'match_details') and sample_match.match_details:
                    print("✓ Enhanced match details present in frontend data")
                    print(f"  Sample match score: {sample_match.match_score}")
                    print(f"  Matching skills: {sample_match.matching_skills[:3]}")
                else:
                    print("⚠ Enhanced match details not found in frontend data")
        else:
            print("⚠ No context data available")
    else:
        print(f"✗ AI job matches view failed with status {response.status_code}")
    
    # Test job list view
    response = client.get('/jobs/')
    
    if response.status_code == 200:
        print("✓ Job list view loaded successfully")
        
        context = response.context
        if context:
            job_matches = context.get('job_matches', [])
            user_skills = context.get('user_skills', set())
            
            print(f"✓ Found {len(user_skills)} user skills in context")
            
            if hasattr(job_matches, 'object_list'):
                matches_count = len(job_matches.object_list)
                print(f"✓ Found {matches_count} job matches in list view")
            else:
                print(f"✓ Found {len(job_matches)} job matches in list view")
    else:
        print(f"✗ Job list view failed with status {response.status_code}")
    
    print("\n=== Frontend Integration Test Complete ===")
    
    # Check JobMatch records
    job_match_count = JobMatch.objects.filter(resume=resume).count()
    print(f"\n📊 Database Status:")
    print(f"  - Total JobMatch records: {job_match_count}")
    print(f"  - Active jobs in DB: {Job.objects.filter(is_active=True).count()}")
    print(f"  - Resume analysis complete: {'✓' if resume.analysis_data else '✗'}")

if __name__ == "__main__":
    test_frontend_integration()
