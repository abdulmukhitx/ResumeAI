#!/usr/bin/env python3
"""
Debug script to test AI Job Matching web functionality
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
from django.utils import timezone

def debug_job_matching():
    """Debug the job matching functionality"""
    print("🔍 Debugging AI Job Matching...")
    
    # Get a test user with resume
    user = User.objects.filter(username='asalachik@gmail.com').first()
    if not user:
        user = User.objects.filter(resumes__isnull=False).first()
    if not user:
        user = User.objects.first()
    
    print(f"✅ User: {user.username}")
    
    # Get user's resume
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        print("❌ No resume found for user")
        return
    
    print(f"✅ Resume ID: {resume.id}")
    print(f"   - File: {resume.file.name if resume.file else 'No file'}")
    print(f"   - Extracted skills: {resume.extracted_skills}")
    print(f"   - Experience level: {resume.experience_level}")
    
    # Check jobs in database
    jobs_count = Job.objects.filter(is_active=True).count()
    total_jobs = Job.objects.count()
    print(f"✅ Jobs in DB: {total_jobs} total, {jobs_count} active")
    
    # Sample some jobs
    sample_jobs = Job.objects.filter(is_active=True)[:3]
    print("\n📋 Sample jobs:")
    for i, job in enumerate(sample_jobs, 1):
        print(f"   {i}. {job.title}")
        print(f"      Company: {job.company_name}")
        print(f"      Location: {job.location}")
        print(f"      Description: {job.description[:100] if job.description else 'None'}...")
    
    # Test basic matching logic
    print("\n🔍 Testing basic matching logic...")
    
    if resume.extracted_skills:
        user_skills = [skill.lower() for skill in resume.extracted_skills]
        print(f"User skills (lowercase): {user_skills}")
        
        for job in sample_jobs:
            job_text = f"{job.title} {job.description or ''} {job.requirements or ''}".lower()
            matched_skills = [skill for skill in user_skills if skill in job_text]
            match_score = 50  # Default
            if matched_skills:
                match_score = min((len(matched_skills) / len(user_skills)) * 100, 100)
            
            print(f"   Job: {job.title}")
            print(f"   Matched skills: {matched_skills}")
            print(f"   Match score: {match_score:.1f}%")
    else:
        print("⚠️  No extracted skills found in resume")
    
    # Check existing JobMatch records
    existing_matches = JobMatch.objects.filter(resume=resume).count()
    print(f"\n📊 Existing JobMatch records: {existing_matches}")
    
    if existing_matches > 0:
        recent_matches = JobMatch.objects.filter(resume=resume).order_by('-created_at')[:3]
        print("Recent matches:")
        for match in recent_matches:
            print(f"   - {match.job.title}: {match.match_score}%")
    
    print("\n🏁 Debug completed!")

if __name__ == "__main__":
    debug_job_matching()
