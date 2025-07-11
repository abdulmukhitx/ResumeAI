#!/usr/bin/env python3
"""
Simple test for job matching functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from resumes.models import Resume
from jobs.models import Job, JobMatch

def test_simple_job_matching():
    """Test simple job matching"""
    print("🧪 Testing Simple Job Matching...")
    
    # Get a test user
    user = User.objects.filter(username='testuser@example.com').first()
    if not user:
        user = User.objects.first()
    
    if not user:
        print("❌ No users found")
        return
    
    print(f"✅ Using user: {user.username}")
    
    # Get user's resume
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        print("❌ No resume found")
        return
    
    print(f"✅ Found resume: {resume.id}")
    
    # Get some jobs
    jobs = Job.objects.filter(is_active=True)[:10]
    print(f"✅ Found {jobs.count()} active jobs")
    
    if not jobs:
        print("❌ No active jobs found")
        return
    
    # Test basic matching
    user_skills = resume.extracted_skills if hasattr(resume, 'extracted_skills') and resume.extracted_skills else ['Python', 'JavaScript']
    print(f"📊 User skills: {user_skills}")
    
    matches_created = 0
    for job in jobs:
        try:
            # Simple skill matching
            job_text = f"{job.title} {job.description or ''} {job.requirements or ''}".lower()
            matched_skills = [skill for skill in user_skills if skill.lower() in job_text]
            
            match_score = 50  # Default
            if user_skills and matched_skills:
                match_score = min((len(matched_skills) / len(user_skills)) * 100, 100)
            
            # Create or update JobMatch
            job_match, created = JobMatch.objects.get_or_create(
                job=job,
                resume=resume,
                defaults={
                    'user': user,
                    'match_score': match_score,
                    'match_details': {'basic_match': True},
                    'matching_skills': matched_skills,
                    'missing_skills': []
                }
            )
            
            if created:
                matches_created += 1
                print(f"✅ Created match for '{job.title}' - Score: {match_score:.1f}%")
            else:
                job_match.match_score = match_score
                job_match.matching_skills = matched_skills
                job_match.save()
                print(f"🔄 Updated match for '{job.title}' - Score: {match_score:.1f}%")
                
        except Exception as e:
            print(f"❌ Error processing job '{job.title}': {e}")
    
    print(f"\n🏁 Completed! Created {matches_created} new matches")
    
    # Show top matches
    top_matches = JobMatch.objects.filter(resume=resume).order_by('-match_score')[:5]
    print(f"\n🎯 Top 5 matches:")
    for i, match in enumerate(top_matches, 1):
        print(f"   {i}. {match.job.title} at {match.job.company_name} - {match.match_score:.1f}%")

if __name__ == "__main__":
    test_simple_job_matching()
