#!/usr/bin/env python
"""
Quick verification of enhanced job matcher fixes
"""

import os
import sys
import django

# Setup Django
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import Resume
from resumes.enhanced_job_matcher import EnhancedJobMatcher

def quick_test():
    print("=== Quick Enhanced Matcher Test ===\n")
    
    User = get_user_model()
    
    # Get an existing user and resume
    user = User.objects.first()
    if not user:
        print("✗ No users found in database")
        return
        
    resume = Resume.objects.filter(user=user, is_active=True).first()
    if not resume:
        print("✗ No active resume found")
        return
        
    print(f"✓ Testing with user: {user.email}")
    print(f"✓ Using resume: {resume.original_filename}")
    
    # Test enhanced matcher
    try:
        enhanced_matcher = EnhancedJobMatcher(user=user, resume=resume)
        
        # Test single job match calculation
        from jobs.models import Job
        test_job = Job.objects.filter(is_active=True).first()
        
        if test_job:
            print(f"✓ Testing with job: {test_job.title}")
            
            # Mock resume analysis for testing
            resume_analysis = {
                'technical_skills': ['Python', 'Django', 'PostgreSQL', 'AWS'],
                'soft_skills': ['Communication', 'Teamwork'],
                'job_titles': ['Developer', 'Engineer'],
                'experience_level': 'senior',
                'education': ['Bachelor'],
                'all_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Communication', 'Teamwork']
            }
            
            match_result = enhanced_matcher.calculate_job_match_score(test_job, resume_analysis)
            
            print(f"✓ Match calculation successful!")
            print(f"  Match Score: {match_result['match_score']:.1f}%")
            print(f"  Match Details Keys: {list(match_result['match_details'].keys())}")
            print(f"  Breakdown Keys: {list(match_result['breakdown'].keys())}")
            
            # Test generate_job_matches
            matches = enhanced_matcher.generate_job_matches(limit=3)
            print(f"✓ Generated {len(matches)} job matches")
            
            if matches:
                for i, match in enumerate(matches[:2], 1):
                    print(f"  Match {i}: {match['job'].title} ({match['match_score']:.1f}%)")
                    print(f"    Matching Skills: {match.get('matching_skills', [])[:3]}")
                    
            print("\n✅ Enhanced matcher working correctly!")
            
        else:
            print("⚠ No active jobs found for testing")
            
    except Exception as e:
        print(f"✗ Enhanced matcher failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
