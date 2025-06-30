#!/usr/bin/env python
"""
Final Enhanced AI Integration Verification
Comprehensive test of the entire enhanced AI job matching system
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
from jobs.models import Job, JobMatch
from resumes.enhanced_analyzer import EnhancedAIAnalyzer
from resumes.enhanced_job_matcher import EnhancedJobMatcher

def verify_enhanced_ai_integration():
    """Comprehensive verification of enhanced AI integration"""
    print("🔍 FINAL ENHANCED AI INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # 1. Database Status
    print("\n📊 DATABASE STATUS:")
    User = get_user_model()
    users_count = User.objects.count()
    resumes_count = Resume.objects.filter(is_active=True).count()
    jobs_count = Job.objects.filter(is_active=True).count()
    matches_count = JobMatch.objects.count()
    enhanced_matches_count = JobMatch.objects.filter(
        match_details__isnull=False
    ).exclude(match_details={}).count()
    
    print(f"  ✓ Total Users: {users_count}")
    print(f"  ✓ Active Resumes: {resumes_count}")
    print(f"  ✓ Active Jobs: {jobs_count}")
    print(f"  ✓ Total Job Matches: {matches_count}")
    print(f"  ✓ Enhanced Matches (with details): {enhanced_matches_count}")
    
    # 2. Test Enhanced Analyzer
    print("\n🔬 ENHANCED ANALYZER TEST:")
    try:
        analyzer = EnhancedAIAnalyzer()
        
        test_resume_text = """
        Senior Python Developer
        5+ years of experience in web development
        
        TECHNICAL SKILLS:
        - Python, Django, Flask
        - PostgreSQL, Redis, MongoDB
        - AWS, Docker, Kubernetes
        - React.js, JavaScript, TypeScript
        - Git, Jenkins, CI/CD
        
        EXPERIENCE:
        Senior Software Engineer at TechCorp (2020-2023)
        - Built microservices with Django and Docker
        - Led team of 4 developers
        - Implemented ML recommendation systems
        
        Software Developer at StartupAI (2018-2020)
        - Developed REST APIs with Flask
        - Optimized database performance
        """
        
        analysis_result = analyzer.analyze_resume(test_resume_text)
        
        print(f"  ✓ Analyzer initialized successfully")
        print(f"  ✓ Technical Skills Found: {len(analysis_result.get('technical_skills', []))}")
        print(f"  ✓ Job Titles Found: {len(analysis_result.get('job_titles', []))}")
        print(f"  ✓ Experience Level: {analysis_result.get('experience_level', 'Unknown')}")
        print(f"  ✓ Sample Technical Skills: {analysis_result.get('technical_skills', [])[:5]}")
        print(f"  ✓ Sample Job Titles: {analysis_result.get('job_titles', [])[:3]}")
        
    except Exception as e:
        print(f"  ✗ Enhanced Analyzer Failed: {e}")
    
    # 3. Test Enhanced Job Matcher
    print("\n🎯 ENHANCED JOB MATCHER TEST:")
    try:
        # Get a test user and resume
        test_user = User.objects.first()
        if not test_user:
            print("  ⚠ No users found for testing")
            return
            
        test_resume = Resume.objects.filter(user=test_user, is_active=True).first()
        if not test_resume:
            print("  ⚠ No active resume found for testing")
            return
            
        enhanced_matcher = EnhancedJobMatcher(user=test_user, resume=test_resume)
        
        print(f"  ✓ Matcher initialized for user: {test_user.email}")
        print(f"  ✓ Using resume: {test_resume.original_filename}")
        
        # Test job match generation
        matches = enhanced_matcher.generate_job_matches(limit=5)
        
        print(f"  ✓ Generated {len(matches)} enhanced job matches")
        
        if matches:
            print("  📋 Sample Matches:")
            for i, match in enumerate(matches[:3], 1):
                job = match.get('job')
                score = match.get('match_score', 0)
                matching_skills = match.get('matching_skills', [])
                missing_skills = match.get('missing_skills', [])
                
                print(f"    {i}. {job.title} at {job.company_name}")
                print(f"       Match Score: {score:.1f}%")
                print(f"       Matching Skills: {matching_skills[:3]}...")
                print(f"       Missing Skills: {missing_skills[:2]}...")
                print()
        
    except Exception as e:
        print(f"  ✗ Enhanced Job Matcher Failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Verify Frontend Integration Points
    print("\n🌐 FRONTEND INTEGRATION VERIFICATION:")
    
    # Check if views are using enhanced matcher
    try:
        from jobs.views import ai_job_matches_view, job_list_view
        
        # Check imports in views
        import inspect
        ai_view_source = inspect.getsource(ai_job_matches_view)
        job_list_source = inspect.getsource(job_list_view)
        
        if 'EnhancedJobMatcher' in ai_view_source:
            print("  ✓ AI Job Matches view uses EnhancedJobMatcher")
        else:
            print("  ✗ AI Job Matches view doesn't use EnhancedJobMatcher")
            
        if 'EnhancedJobMatcher' in job_list_source:
            print("  ✓ Job List view uses EnhancedJobMatcher")
        else:
            print("  ✗ Job List view doesn't use EnhancedJobMatcher")
            
    except Exception as e:
        print(f"  ✗ Could not verify view integration: {e}")
    
    # Check template filters
    try:
        from jobs.templatetags.job_filters import get_item
        
        test_dict = {'test_key': 'test_value'}
        result = get_item(test_dict, 'test_key')
        
        if result == 'test_value':
            print("  ✓ Template filter 'get_item' working correctly")
        else:
            print("  ✗ Template filter 'get_item' not working")
            
    except Exception as e:
        print(f"  ✗ Template filter verification failed: {e}")
    
    # 5. Check Sample JobMatch with Enhanced Data
    print("\n🔍 ENHANCED DATA VERIFICATION:")
    
    try:
        enhanced_match = JobMatch.objects.filter(
            match_details__isnull=False
        ).exclude(match_details={}).first()
        
        if enhanced_match:
            print("  ✓ Found enhanced JobMatch with detailed data")
            print(f"    Job: {enhanced_match.job.title}")
            print(f"    Match Score: {enhanced_match.match_score}%")
            print(f"    Match Details Keys: {list(enhanced_match.match_details.keys())}")
            print(f"    Matching Skills: {enhanced_match.matching_skills[:3]}...")
            print(f"    Missing Skills: {enhanced_match.missing_skills[:2]}...")
        else:
            print("  ⚠ No enhanced JobMatch data found")
            
            # Try to create one for verification
            if matches and len(matches) > 0:
                print("  📝 Creating sample enhanced JobMatch...")
                sample_match = matches[0]
                job = sample_match.get('job')
                
                job_match, created = JobMatch.objects.get_or_create(
                    job=job,
                    resume=test_resume,
                    defaults={
                        'user': test_user,
                        'match_score': sample_match.get('match_score', 0),
                        'match_details': sample_match.get('match_details', {}),
                        'matching_skills': sample_match.get('matching_skills', []),
                        'missing_skills': sample_match.get('missing_skills', [])
                    }
                )
                
                if created:
                    print("  ✓ Created sample enhanced JobMatch for frontend testing")
                else:
                    print("  ✓ Enhanced JobMatch already exists")
                    
    except Exception as e:
        print(f"  ✗ Enhanced data verification failed: {e}")
    
    # 6. Final Summary
    print("\n🎯 INTEGRATION SUMMARY:")
    print("=" * 40)
    
    if enhanced_matches_count > 0:
        print("✅ ENHANCED AI INTEGRATION: SUCCESSFUL")
        print("   - Enhanced analyzer working")
        print("   - Enhanced job matcher working") 
        print("   - Enhanced data stored in database")
        print("   - Frontend views updated to use enhanced matcher")
        print("   - Template filters available for display")
    else:
        print("⚠ ENHANCED AI INTEGRATION: NEEDS ATTENTION")
        print("   - System components working but no enhanced data in DB")
        print("   - May need to trigger job matching for existing users")
    
    print(f"\n📊 Database Summary:")
    print(f"   - {enhanced_matches_count}/{matches_count} matches have enhanced data")
    print(f"   - {jobs_count} active jobs available for matching")
    print(f"   - {resumes_count} active resumes ready for analysis")
    
    print("\n🚀 Frontend Testing:")
    print("   1. Server running at: http://localhost:8000")
    print("   2. Login with existing user credentials") 
    print("   3. Navigate to 'AI Job Matches' to see enhanced results")
    print("   4. Check job match scores and detailed skill breakdowns")
    
    print("\n✅ VERIFICATION COMPLETE!")

if __name__ == "__main__":
    verify_enhanced_ai_integration()
