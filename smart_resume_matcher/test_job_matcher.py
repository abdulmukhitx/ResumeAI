"""
Test the JobMatcher functionality with a mock resume and job data
"""

import sys
import os
import json
from django.utils import timezone
from datetime import datetime

# Add the project path to Python path
project_path = os.path.abspath(os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Setup Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.job_matcher import JobMatcher
from resumes.models import Resume
from jobs.models import Job, JobMatch
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_resume():
    """Create a test resume with sample data"""
    # Try to get existing user or create a new one
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        # Create user with set_password to properly hash the password
        user = User.objects.create(
            username='testuser',
            email='test@example.com',
            is_active=True
        )
        user.set_password('password123')
        user.save()
    
    # Create or get a test resume
    resume = Resume.objects.filter(user=user).first()
    if not resume:
        # Get fields dynamically to avoid issues if model changes
        required_fields = {
            'user': user,
            'original_filename': 'test_resume.pdf',
            'status': 'completed',
            'raw_text': 'Python developer with 5 years of experience in Django, Flask and FastAPI.'
        }
        
        # Only add optional fields if they exist on the model
        resume = Resume(**required_fields)
        
        # Set other fields if they exist on the model
        if hasattr(resume, 'extracted_skills'):
            resume.extracted_skills = ['python', 'django', 'flask', 'fastapi', 'rest api', 'git']
        
        if hasattr(resume, 'experience_level'):
            resume.experience_level = 'middle'
            
        if hasattr(resume, 'job_titles'):
            resume.job_titles = ['Senior Python Developer', 'Backend Engineer']
            
        if hasattr(resume, 'education'):
            resume.education = [{"degree": "Bachelor", "institution": "Test University", "year": "2020"}]
            
        if hasattr(resume, 'work_experience'):
            resume.work_experience = [
                {
                    "position": "Python Developer",
                    "company": "Tech Company",
                    "duration": "2018-2022",
                    "key_responsibilities": ["Developed Django applications", "API development"]
                }
            ]
            
        if hasattr(resume, 'analysis_summary'):
            resume.analysis_summary = "Mid-level Python developer with strong backend skills"
            
        if hasattr(resume, 'confidence_score'):
            resume.confidence_score = 0.95
            
        # Save the resume
        resume.save()
    
    return resume

def create_test_jobs():
    """Create test jobs with different match levels"""
    
    # Good match job
    good_job, _ = Job.objects.get_or_create(
        hh_id='good_match_job',
        defaults={
            'title': 'Python Backend Developer',
            'company_name': 'Good Match Corp',
            'description': """Looking for Python developer with Django experience.
            Requirements: Python, Django, Flask, RESTful APIs, Git, SQL.
            Responsibilities include maintaining backend services.""",
            'requirements': 'Python, Django, RESTful APIs, Git',
            'location': 'Moscow',
            'published_at': timezone.now(),
            'hh_url': 'https://example.com/job1',
            'is_active': True
        }
    )
    
    # Medium match job
    medium_job, _ = Job.objects.get_or_create(
        hh_id='medium_match_job',
        defaults={
            'title': 'Full Stack Engineer',
            'company_name': 'Medium Match Corp',
            'description': """Looking for a full stack developer with Python and JavaScript skills.
            Requirements: Python, React, Node.js, JavaScript, HTML, CSS.
            Responsibilities include developing web applications.""",
            'requirements': 'Python, React, JavaScript',
            'location': 'Moscow',
            'published_at': timezone.now(),
            'hh_url': 'https://example.com/job2',
            'is_active': True
        }
    )
    
    # Poor match job
    poor_job, _ = Job.objects.get_or_create(
        hh_id='poor_match_job',
        defaults={
            'title': 'DevOps Engineer',
            'company_name': 'Poor Match Corp',
            'description': """Looking for a DevOps engineer with Kubernetes experience.
            Requirements: Docker, Kubernetes, AWS, CI/CD, Terraform.
            Responsibilities include managing cloud infrastructure.""",
            'requirements': 'Docker, Kubernetes, AWS, Terraform',
            'location': 'Moscow',
            'published_at': timezone.now(),
            'hh_url': 'https://example.com/job3',
            'is_active': True
        }
    )
    
    return [good_job, medium_job, poor_job]

def test_job_matcher():
    """Test the JobMatcher functionality"""
    print("======== Testing JobMatcher ========")
    
    try:
        # Create test data
        test_resume = create_test_resume()
        test_jobs = create_test_jobs()
        
        # Initialize JobMatcher
        matcher = JobMatcher(user=test_resume.user, resume=test_resume)
        
        # Test generate_search_query_from_resume
        search_query = matcher.generate_search_query_from_resume()
        print(f"Generated search query: {search_query}")
        
        # Test match calculation for each job
        for job in test_jobs:
            job_data = {
                'id': job.hh_id,
                'name': job.title,
                'description': job.description,
                'snippet': {
                    'requirement': job.requirements,
                    'responsibility': job.description
                },
                'employer': {
                    'name': job.company_name,
                    'alternate_url': 'https://example.com'
                },
                'area': {
                    'name': job.location
                },
                'salary': {
                    'from': None,
                    'to': None,
                    'currency': 'RUB'
                },
                'alternate_url': 'https://example.com/job'
            }
            
            match_score, match_details = matcher.calculate_match_score(job_data)
            
            print(f"\nJob: {job.title}")
            print(f"Match Score: {match_score:.1f}")
            print(f"Skill Score: {match_details['skill_score']}")
            print(f"Experience Score: {match_details['experience_score']}")
            print(f"Matching Skills: {', '.join(match_details['matching_skills'])}")
            print(f"Missing Skills: {', '.join(match_details['missing_skills'])}")
            
            try:
                # Update or create JobMatch
                JobMatch.objects.update_or_create(
                    job=job,
                    resume=test_resume,
                    defaults={
                        'user': test_resume.user,
                        'match_score': match_score,
                        'match_details': match_details,
                        'matching_skills': match_details.get('matching_skills', []),
                        'missing_skills': match_details.get('missing_skills', [])
                    }
                )
                print("JobMatch record created/updated successfully")
            except Exception as e:
                print(f"Error creating JobMatch: {str(e)}")
    
    except Exception as e:
        print(f"Error in test_job_matcher: {str(e)}")
    
    print("\n======== Test Complete ========")

if __name__ == '__main__':
    test_job_matcher()
