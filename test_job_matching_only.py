#!/usr/bin/env python3
"""
Test Enhanced Job Matching Specifically
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
from jobs.models import Job
import json

def test_job_matching():
    print("🎯 Testing Enhanced Job Matching")
    print("=" * 40)
    
    # Get test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='enhanced_test_user',
        defaults={'email': 'enhanced_test@example.com'}
    )
    
    # Create test resume with Python/Django skills
    enhanced_analysis = {
        'extracted_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker', 'React'],
        'programming_languages': ['Python'],
        'frameworks_libraries': ['Django', 'React'],
        'databases': ['PostgreSQL'],
        'cloud_platforms': ['AWS'],
        'tools_technologies': ['Docker'],
        'experience_level': 'senior',
        'tech_stack_focus': 'Python Backend Development',
        'specialization': 'Backend Python/Django Development'
    }
    
    # Clean up any existing test resume
    Resume.objects.filter(user=user).delete()
    
    resume = Resume.objects.create(
        user=user,
        original_filename='enhanced_test.pdf',
        status='completed',
        extracted_skills=enhanced_analysis['extracted_skills'],
        experience_level=enhanced_analysis['experience_level'],
        analysis_summary=json.dumps(enhanced_analysis)
    )
    
    print(f"✅ Created test resume for user: {user.username}")
    print(f"📊 Resume skills: {enhanced_analysis['extracted_skills']}")
    print(f"🎨 Specialization: {enhanced_analysis['specialization']}")
    
    # Test job matching
    matcher = EnhancedJobMatcher(user, resume)
    
    # Get jobs and test individual job scoring
    jobs = Job.objects.all()[:5]
    print(f"\n🔍 Testing against {len(jobs)} jobs:")
    
    for job in jobs:
        try:
            match_result = matcher.calculate_job_match_score(job, enhanced_analysis)
            score = match_result['match_score']
            details = match_result['match_details']
            
            print(f"\n📋 {job.title} at {job.company_name}")
            print(f"   🎯 Match Score: {score:.1f}%")
            if details['matched_skills']:
                print(f"   ✅ Matched Skills: {', '.join(details['matched_skills'][:3])}")
            if details['missing_skills']:
                print(f"   ❌ Missing Skills: {', '.join(details['missing_skills'][:3])}")
            print(f"   📈 Experience Match: {'✅' if details['experience_match'] else '❌'}")
            
        except Exception as e:
            print(f"   ❌ Error matching job {job.title}: {e}")
    
    # Test full job matching workflow
    print(f"\n🚀 Testing Full Job Matching Workflow...")
    try:
        matches = matcher.generate_job_matches(limit=10)
        print(f"✅ Generated {len(matches)} job matches")
        
        if matches:
            print(f"\n🏆 Top 3 Job Matches:")
            for i, match in enumerate(matches[:3], 1):
                job = match['job']
                score = match['match_score']
                details = match['match_details']
                print(f"  {i}. {job.title} - {score:.1f}% match")
                print(f"     Company: {job.company_name}")
                print(f"     Matched Skills: {', '.join(details['matched_skills'][:3])}")
        
        # Test saving matches
        print(f"\n💾 Testing Save Job Matches...")
        matcher._save_job_matches(matches, enhanced_analysis)
        print("✅ Job matches saved to database")
        
    except Exception as e:
        print(f"❌ Error in full workflow: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Enhanced Job Matching Test Complete!")

if __name__ == "__main__":
    test_job_matching()
