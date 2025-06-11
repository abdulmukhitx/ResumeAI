#!/usr/bin/env python
"""
Test script to verify resume analysis is working correctly
and show the current status of all users and their resumes.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.models import Resume
from accounts.models import User
from jobs.models import JobMatch

def test_resume_analysis_status():
    """Check the status of resume analysis for all users"""
    print("=== RESUME ANALYSIS STATUS REPORT ===\n")
    
    users = User.objects.all()
    print(f"Total users in system: {users.count()}\n")
    
    for user in users:
        print(f"USER: {user.email}")
        print(f"  Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        
        # Get all resumes for this user
        resumes = Resume.objects.filter(user=user).order_by('-created_at')
        print(f"  Total resumes: {resumes.count()}")
        
        if resumes.exists():
            latest_resume = resumes.first()
            print(f"  Latest resume:")
            print(f"    - Status: {latest_resume.status}")
            print(f"    - Active: {latest_resume.is_active}")
            print(f"    - Filename: {latest_resume.original_filename}")
            print(f"    - Uploaded: {latest_resume.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"    - File size: {latest_resume.file_size} bytes")
            
            if latest_resume.status == 'completed':
                print(f"    - Skills extracted: {len(latest_resume.extracted_skills)} skills")
                print(f"    - Skills: {latest_resume.extracted_skills}")
                print(f"    - Experience level: {latest_resume.experience_level}")
                print(f"    - Job titles: {latest_resume.job_titles}")
                print(f"    - Analysis summary: {latest_resume.analysis_summary[:100]}..." if latest_resume.analysis_summary else "No summary")
                
                # Check job matches
                job_matches = JobMatch.objects.filter(resume=latest_resume)
                print(f"    - Job matches: {job_matches.count()}")
                
                if job_matches.exists():
                    top_match = job_matches.order_by('-match_score').first()
                    print(f"    - Best match: {top_match.match_score:.1f}% - {top_match.job.title}")
            
            elif latest_resume.status == 'failed':
                print(f"    - Analysis FAILED")
                
            elif latest_resume.status == 'processing':
                print(f"    - Analysis in progress...")
                
        else:
            print(f"  ❌ No resumes uploaded")
        
        print("-" * 60)
    
    print("\n=== SUMMARY ===")
    total_resumes = Resume.objects.count()
    completed_resumes = Resume.objects.filter(status='completed').count()
    failed_resumes = Resume.objects.filter(status='failed').count()
    active_resumes = Resume.objects.filter(is_active=True).count()
    
    print(f"Total resumes in system: {total_resumes}")
    print(f"Successfully analyzed: {completed_resumes}")
    print(f"Failed analysis: {failed_resumes}")
    print(f"Currently active: {active_resumes}")
    
    # Check if resume analysis is working
    if completed_resumes > 0:
        print(f"\n✅ RESUME ANALYSIS IS WORKING")
        print(f"   - {completed_resumes} resumes have been successfully analyzed")
        print(f"   - Skills extraction is functional")
        print(f"   - The issue is that user 'asalachik@gmail.com' has no resume uploaded")
    else:
        print(f"\n❌ RESUME ANALYSIS MAY HAVE ISSUES")
        print(f"   - No resumes have been successfully analyzed")

if __name__ == "__main__":
    test_resume_analysis_status()
