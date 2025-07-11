#!/usr/bin/env python3
"""
Test the exact view logic that runs when Auto-Match is clicked
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from resumes.models import Resume
from jobs.models import Job, JobMatch, JobSearch
from django.utils import timezone

def test_auto_match_logic():
    """Test the exact logic from the ai_job_matches_view"""
    print("🧪 Testing Auto-Match Logic...")
    
    # Get user and resume (same as view)
    user = User.objects.filter(username='asalachik@gmail.com').first()
    user_resume = Resume.objects.filter(user=user, is_active=True).first()
    
    if not user_resume:
        user_resume = Resume.objects.filter(user=user).first()
    
    print(f"✅ User: {user.username}")
    print(f"✅ Resume: {user_resume.id}")
    
    # Initialize variables (same as view)
    jobs = []
    search_performed = True
    search_query = ""
    location = ""
    auto_search = True
    
    # Create JobSearch record (same as view)
    job_search = JobSearch.objects.create(
        user=user,
        resume=user_resume,
        search_query=search_query,
        location=location,
        status='processing',
        started_at=timezone.now()
    )
    print(f"✅ Created JobSearch: {job_search.id}")
    
    try:
        # Exact logic from the view
        print("🔍 Getting jobs from database...")
        all_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:50]
        print(f"   Found {len(all_jobs)} active jobs")
        
        if not all_jobs:
            print("❌ No active jobs found")
            return
        
        # Get user skills
        user_skills = []
        if hasattr(user_resume, 'extracted_skills') and user_resume.extracted_skills:
            user_skills = user_resume.extracted_skills
        
        print(f"✅ User skills: {user_skills}")
        
        # Process each job (exact view logic)
        for job in all_jobs:
            jobs.append(job)
            
            # Create basic JobMatch record
            match_score = 50  # Default score for now
            matched_skills = []
            
            if user_skills:
                # Simple skill matching
                job_text = f"{job.title} {job.description or ''} {job.requirements or ''}".lower()
                matched_skills = [skill for skill in user_skills if skill.lower() in job_text]
                if matched_skills:
                    match_score = min((len(matched_skills) / len(user_skills)) * 100, 100)
            
            # Ensure JobMatch object exists
            job_match, created = JobMatch.objects.get_or_create(
                job=job,
                resume=user_resume,
                defaults={
                    'user': user,
                    'match_score': match_score,
                    'match_details': {'basic_match': True},
                    'matching_skills': matched_skills,
                    'missing_skills': []
                }
            )
            
            # Update existing match
            if not created:
                job_match.match_score = match_score
                job_match.matching_skills = matched_skills
                job_match.save()
            
            if created or matched_skills:
                print(f"   {'✅ Created' if created else '🔄 Updated'} match for: {job.title} ({match_score:.1f}%) - Skills: {matched_skills}")
        
        # Update JobSearch record
        job_search.total_found = len(jobs)
        job_search.jobs_analyzed = len(jobs)
        job_search.matches_found = len(jobs)
        job_search.status = 'completed'
        job_search.completed_at = timezone.now()
        job_search.save()
        
        print(f"✅ Updated JobSearch - Found: {len(jobs)} matches")
        
        # Check created JobMatch records
        total_matches = JobMatch.objects.filter(resume=user_resume).count()
        high_matches = JobMatch.objects.filter(resume=user_resume, match_score__gte=70).count()
        medium_matches = JobMatch.objects.filter(resume=user_resume, match_score__gte=50, match_score__lt=70).count()
        
        print(f"\n📊 Final Results:")
        print(f"   Total JobMatch records: {total_matches}")
        print(f"   High matches (70%+): {high_matches}")
        print(f"   Medium matches (50-69%): {medium_matches}")
        
        # Show top matches
        top_matches = JobMatch.objects.filter(resume=user_resume).order_by('-match_score')[:5]
        print(f"\n🏆 Top 5 matches:")
        for i, match in enumerate(top_matches, 1):
            print(f"   {i}. {match.job.title} - {match.match_score:.1f}% - Skills: {match.matching_skills}")
        
        print(f"\n🎉 Auto-Match completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auto_match_logic()
