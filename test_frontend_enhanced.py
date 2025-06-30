#!/usr/bin/env python
"""
Simple Frontend Integration Test
Tests the enhanced AI job matching frontend display
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
from resumes.enhanced_job_matcher import EnhancedJobMatcher

def test_frontend_enhanced_display():
    """Test that enhanced AI results are properly displayed in frontend"""
    print("=== Testing Enhanced AI Frontend Display ===\n")
    
    # Get or create test user
    User = get_user_model()
    test_user, created = User.objects.get_or_create(
        email='test_frontend@example.com',
        defaults={
            'username': 'test_frontend_user',
            'password': 'testpass123'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✓ Created test user: {test_user.username}")
    else:
        print(f"✓ Using existing test user: {test_user.username}")
    
    # Look for existing resume or create a basic one
    resume = Resume.objects.filter(user=test_user, is_active=True).first()
    
    if not resume:
        print("ℹ  No resume found for user. Creating one with existing skills...")
        # Create a basic resume with enhanced analysis data
        resume = Resume.objects.create(
            user=test_user,
            original_filename="test_resume.pdf",
            status='completed',
            raw_text="Senior Python Developer with Django, PostgreSQL, AWS experience",
            extracted_skills=[
                'Python', 'Django', 'PostgreSQL', 'AWS', 'Docker', 
                'JavaScript', 'React', 'Git', 'Linux', 'REST APIs'
            ],
            experience_level='senior',
            job_titles=['Senior Python Developer', 'Software Engineer', 'Backend Developer'],
            analysis_summary="Experienced backend developer with strong Python and web development skills",
            confidence_score=0.95,
            is_active=True
        )
        print(f"✓ Created test resume with enhanced data")
    else:
        print(f"✓ Using existing resume: {resume.original_filename}")
        
        # Ensure resume has enhanced data
        if not resume.extracted_skills:
            resume.extracted_skills = [
                'Python', 'Django', 'PostgreSQL', 'AWS', 'Docker', 
                'JavaScript', 'React', 'Git', 'Linux', 'REST APIs'
            ]
            resume.experience_level = 'senior'
            resume.job_titles = ['Senior Python Developer', 'Software Engineer', 'Backend Developer']
            resume.save()
            print("✓ Updated resume with enhanced skills data")
    
    # Test enhanced job matching
    print("\n--- Testing Enhanced Job Matching ---")
    enhanced_matcher = EnhancedJobMatcher(user=test_user, resume=resume)
    
    # Check if we have jobs in the database
    job_count = Job.objects.filter(is_active=True).count()
    print(f"ℹ  Available jobs in database: {job_count}")
    
    if job_count == 0:
        print("⚠  No jobs in database. Creating sample jobs...")
        # Create sample jobs for testing
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company_name': 'Tech Solutions Inc',
                'description': 'Looking for a Senior Python Developer with Django and PostgreSQL experience',
                'requirements': 'Python, Django, PostgreSQL, AWS, Docker required',
                'location': 'San Francisco, CA',
                'hh_id': 'test_job_1',
                'is_active': True
            },
            {
                'title': 'Full Stack Developer',
                'company_name': 'Digital Innovations',
                'description': 'Full stack developer needed with React and Python skills',
                'requirements': 'React, JavaScript, Python, REST APIs, Git',
                'location': 'New York, NY',
                'hh_id': 'test_job_2',
                'is_active': True
            },
            {
                'title': 'DevOps Engineer',
                'company_name': 'Cloud Systems Corp',
                'description': 'DevOps engineer with AWS and Docker experience',
                'requirements': 'AWS, Docker, Kubernetes, Linux, Python',
                'location': 'Austin, TX',
                'hh_id': 'test_job_3',
                'is_active': True
            }
        ]
        
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                hh_id=job_data['hh_id'],
                defaults=job_data
            )
            if created:
                print(f"  ✓ Created job: {job.title}")
    
    # Generate enhanced job matches
    enhanced_matches = enhanced_matcher.generate_job_matches(limit=10)
    
    if enhanced_matches:
        print(f"✓ Generated {len(enhanced_matches)} enhanced job matches")
        
        # Create JobMatch objects for frontend display
        for match_data in enhanced_matches:
            job = match_data.get('job')
            if job:
                job_match, created = JobMatch.objects.get_or_create(
                    job=job,
                    resume=resume,
                    defaults={
                        'user': test_user,
                        'match_score': match_data.get('match_score', 0),
                        'match_details': match_data.get('match_details', {}),
                        'matching_skills': match_data.get('matching_skills', []),
                        'missing_skills': match_data.get('missing_skills', [])
                    }
                )
                
                if created:
                    print(f"  ✓ Created JobMatch: {job.title} ({match_data.get('match_score', 0):.1f}%)")
                else:
                    # Update with latest enhanced data
                    job_match.match_score = match_data.get('match_score', job_match.match_score)
                    job_match.match_details = match_data.get('match_details', job_match.match_details)
                    job_match.matching_skills = match_data.get('matching_skills', job_match.matching_skills)
                    job_match.missing_skills = match_data.get('missing_skills', job_match.missing_skills)
                    job_match.save()
                    print(f"  ✓ Updated JobMatch: {job.title} ({match_data.get('match_score', 0):.1f}%)")
    else:
        print("⚠ No enhanced matches generated")
    
    # Test frontend views
    print("\n--- Testing Frontend Views ---")
    client = Client()
    
    # Test AI job matches view (without login - should redirect)
    response = client.get('/jobs/ai-matches/')
    if response.status_code == 302:
        print("✓ AI job matches view properly redirects unauthenticated users")
    else:
        print(f"⚠ Unexpected response for unauthenticated request: {response.status_code}")
    
    # Test job list view (without login - should redirect)  
    response = client.get('/jobs/')
    if response.status_code == 302:
        print("✓ Job list view properly redirects unauthenticated users")
    else:
        print(f"⚠ Unexpected response for unauthenticated request: {response.status_code}")
    
    print("\n--- Testing With Django Test Client ---")
    
    # Login the user with Django's built-in authentication
    login_success = client.login(email='test_frontend@example.com', password='testpass123')
    if login_success:
        print("✓ Successfully logged in test user")
        
        # Test AI job matches view with authentication
        response = client.get('/jobs/ai-matches/?auto_search=true')
        
        if response.status_code == 200:
            print("✓ AI job matches view loaded successfully with auth")
            
            # Check response content for enhanced data
            content = response.content.decode('utf-8')
            
            if 'match_score' in content.lower() or 'percentage' in content.lower():
                print("✓ Enhanced match scores visible in HTML")
            else:
                print("⚠ Match scores not found in HTML response")
                
            if 'matching skills' in content.lower():
                print("✓ Enhanced matching skills visible in HTML")
            else:
                print("⚠ Matching skills section not found in HTML")
                
        else:
            print(f"✗ AI job matches view failed with status {response.status_code}")
            
        # Test job list view with authentication
        response = client.get('/jobs/')
        
        if response.status_code == 200:
            print("✓ Job list view loaded successfully with auth")
        else:
            print(f"✗ Job list view failed with status {response.status_code}")
            
    else:
        print("✗ Failed to login test user")
    
    print("\n=== Frontend Integration Test Complete ===")
    
    # Final status check
    job_match_count = JobMatch.objects.filter(resume=resume).count()
    enhanced_matches_count = JobMatch.objects.filter(
        resume=resume,
        match_details__isnull=False
    ).exclude(match_details={}).count()
    
    print(f"\n📊 Final Status:")
    print(f"  - Total JobMatch records: {job_match_count}")
    print(f"  - Enhanced matches (with details): {enhanced_matches_count}")
    print(f"  - Active jobs in DB: {Job.objects.filter(is_active=True).count()}")
    print(f"  - Resume skills count: {len(resume.extracted_skills) if resume.extracted_skills else 0}")
    
    if enhanced_matches_count > 0:
        print("✅ SUCCESS: Enhanced AI data is available for frontend display")
    else:
        print("⚠ WARNING: No enhanced match data found")

if __name__ == "__main__":
    test_frontend_enhanced_display()
