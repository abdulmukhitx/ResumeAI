#!/usr/bin/env python3
"""
Test Enhanced AI Integration - Verify improved skill extraction and job matching
"""

import os
import sys
import django
import json
import logging

# Setup Django
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from resumes.models import Resume
from resumes.enhanced_analyzer import EnhancedAIAnalyzer
from resumes.enhanced_job_matcher import EnhancedJobMatcher
from jobs.models import Job

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_analyzer():
    """Test the enhanced analyzer with a sample resume text"""
    print("🧠 Testing Enhanced AI Analyzer...")
    
    sample_resume = """
    John Doe
    Senior Python Developer
    
    EXPERIENCE:
    Senior Backend Developer at TechCorp (2020-2023)
    - Developed REST APIs using Django and Django REST Framework
    - Worked with PostgreSQL databases and Redis for caching
    - Built microservices using Docker and deployed on AWS EC2
    - Implemented CI/CD pipelines with Jenkins and GitHub Actions
    - Collaborated with frontend team using React and TypeScript
    
    Python Developer at StartupXYZ (2018-2020)
    - Built web applications using Flask and SQLAlchemy
    - Worked with MongoDB and implemented Elasticsearch for search
    - Experience with Celery for background task processing
    - Used Git for version control
    
    SKILLS:
    - Programming Languages: Python, JavaScript, TypeScript
    - Web Frameworks: Django, Flask, FastAPI
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS (EC2, S3, RDS), Docker, Kubernetes
    - Tools: Git, Jenkins, GitHub Actions
    
    EDUCATION:
    Bachelor of Science in Computer Science
    University of Technology, 2018
    """
    
    analyzer = EnhancedAIAnalyzer()
    analysis = analyzer.analyze_resume(sample_resume)
    
    print("\n📊 Enhanced Analysis Results:")
    print("=" * 50)
    
    # Print key results
    for key, value in analysis.items():
        if key in ['extracted_skills', 'programming_languages', 'frameworks_libraries', 
                  'databases', 'cloud_platforms', 'tools_technologies']:
            print(f"{key.replace('_', ' ').title()}: {len(value)} items")
            for skill in value[:5]:  # Show first 5
                print(f"  - {skill}")
            if len(value) > 5:
                print(f"  ... and {len(value) - 5} more")
            print()
        elif key in ['tech_stack_focus', 'specialization', 'experience_level']:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"Confidence Score: {analysis.get('confidence_score', 0):.2f}")
    
    return analysis

def test_job_matching():
    """Test enhanced job matching"""
    print("\n🎯 Testing Enhanced Job Matching...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    # Create a mock resume with enhanced analysis
    enhanced_analysis = {
        'extracted_skills': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Docker', 'Redis', 'JavaScript'],
        'programming_languages': ['Python', 'JavaScript'],
        'frameworks_libraries': ['Django', 'Flask'],
        'databases': ['PostgreSQL', 'Redis'],
        'cloud_platforms': ['AWS'],
        'tools_technologies': ['Docker', 'Git'],
        'experience_level': 'senior',
        'tech_stack_focus': 'Python Backend Development',
        'specialization': 'Backend Python/Django'
    }
    
    # Get or create a test resume
    resume, created = Resume.objects.get_or_create(
        user=user,
        original_filename='test_resume.pdf',
        defaults={
            'status': 'completed',
            'extracted_skills': enhanced_analysis['extracted_skills'],
            'experience_level': enhanced_analysis['experience_level'],
            'analysis_summary': json.dumps(enhanced_analysis)
        }
    )
    
    # Create enhanced job matcher
    matcher = EnhancedJobMatcher(user, resume)
    
    # Test with existing jobs
    jobs_count = Job.objects.count()
    print(f"Found {jobs_count} jobs in database")
    
    if jobs_count > 0:
        # Generate matches
        matches = matcher.generate_job_matches(limit=10)
        
        print(f"\n🎯 Generated {len(matches)} job matches:")
        
        for i, match in enumerate(matches[:5], 1):
            job = match['job']
            score = match['match_score']
            details = match['match_details']
            
            print(f"\n{i}. {job.title} at {job.company}")
            print(f"   Match Score: {score:.1f}%")
            print(f"   Matched Skills: {', '.join(details['matched_skills'][:3])}")
            if details['missing_skills']:
                print(f"   Missing Skills: {', '.join(details['missing_skills'][:3])}")
            print(f"   Experience Match: {details['experience_match']}")
            
        # Get recommendations summary
        summary = matcher.get_recommendations_summary(matches)
        print(f"\n📈 Recommendations Summary:")
        print(f"   Total Matches: {summary['total_matches']}")
        print(f"   High Quality Matches: {summary['high_quality_matches']}")
        print(f"   Medium Quality Matches: {summary['medium_quality_matches']}")
        if summary['top_skill_gaps']:
            print(f"   Top Skill Gaps: {', '.join(summary['top_skill_gaps'][:3])}")
        print(f"   Recommendation: {summary['recommendation']}")
    else:
        print("No jobs found in database to match against")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced AI Integration")
    print("=" * 60)
    
    try:
        # Test enhanced analyzer
        analysis = test_enhanced_analyzer()
        
        # Test job matching
        test_job_matching()
        
        print("\n✅ Enhanced AI Integration Test Completed Successfully!")
        print("\nKey Improvements:")
        print("- More specific skill extraction with context awareness")
        print("- Better technology stack identification")
        print("- Intelligent job matching based on actual skills")
        print("- Detailed match scoring and explanations")
        print("- Enhanced missing skills identification")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
