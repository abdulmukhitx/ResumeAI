#!/usr/bin/env python3
"""
Quick Enhanced AI Integration Verification
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
from resumes.enhanced_analyzer import EnhancedAIAnalyzer
from resumes.enhanced_job_matcher import EnhancedJobMatcher
from jobs.models import Job
import json

def test_enhanced_system():
    print("🧪 Quick Enhanced AI System Test")
    print("=" * 40)
    
    # Test 1: Enhanced Analyzer
    print("1️⃣ Testing Enhanced Analyzer...")
    analyzer = EnhancedAIAnalyzer()
    
    test_resume = "Senior Python developer with Django, PostgreSQL, AWS experience"
    result = analyzer.enhanced_skill_extraction(test_resume)
    
    print("   ✅ Skills extracted:")
    for category, skills in result.items():
        print(f"     {category}: {skills}")
    
    # Test 2: Check if jobs exist
    print("\n2️⃣ Checking Job Database...")
    job_count = Job.objects.count()
    print(f"   📊 Jobs in database: {job_count}")
    
    if job_count > 0:
        sample_job = Job.objects.first()
        print(f"   📝 Sample job: {sample_job.title} at {sample_job.company_name}")
    
    # Test 3: Enhanced Job Matcher
    print("\n3️⃣ Testing Enhanced Job Matcher...")
    
    # Get or create test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='test_enhanced',
        defaults={'email': 'test@example.com'}
    )
    
    # Create mock resume
    enhanced_analysis = {
        'extracted_skills': ['Python', 'Django', 'PostgreSQL', 'AWS'],
        'programming_languages': ['Python'],
        'frameworks_libraries': ['Django'],
        'databases': ['PostgreSQL'],
        'cloud_platforms': ['AWS'],
        'experience_level': 'senior',
        'tech_stack_focus': 'Python Backend Development'
    }
    
    resume, created = Resume.objects.get_or_create(
        user=user,
        original_filename='test_enhanced.pdf',
        defaults={
            'status': 'completed',
            'extracted_skills': enhanced_analysis['extracted_skills'],
            'experience_level': enhanced_analysis['experience_level'],
            'analysis_summary': json.dumps(enhanced_analysis)
        }
    )
    
    if job_count > 0:
        # Test job matching
        matcher = EnhancedJobMatcher(user, resume)
        matches = matcher.generate_job_matches(limit=5)
        
        print(f"   🎯 Generated {len(matches)} job matches")
        
        for i, match in enumerate(matches[:3], 1):
            job = match['job']
            score = match['match_score']
            print(f"     {i}. {job.title} - {score:.1f}% match")
    else:
        print("   ⚠️ No jobs in database to match against")
    
    print("\n✅ Enhanced AI System Test Complete!")
    return True

if __name__ == "__main__":
    try:
        test_enhanced_system()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
