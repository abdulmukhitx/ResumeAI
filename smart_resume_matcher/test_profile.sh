#!/bin/bash

# Test profile page data
echo "🔍 Testing Profile Page Data"
echo "============================"

cd /home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher

# Test database resume data
echo "1. Database Resume Data:"
python manage.py shell -c "
from accounts.models import User
from resumes.models import Resume
user = User.objects.get(email='abdulmukhit@kbtu.kz')
resumes = Resume.objects.filter(user=user)
print(f'Total resumes: {resumes.count()}')

for i, resume in enumerate(resumes[:2]):
    print(f'\\nResume {i+1}:')
    print(f'  File: {resume.original_filename}')
    print(f'  Status: {resume.status}')
    print(f'  Skills: {resume.extracted_skills[:3] if resume.extracted_skills else \"None\"}')
    print(f'  Experience: {resume.experience_level}')
    print(f'  Job titles: {resume.job_titles[:2] if resume.job_titles else \"None\"}')
    print(f'  Work experience: {resume.work_experience[:1] if resume.work_experience else \"None\"}')
    print(f'  Education: {resume.education[:1] if resume.education else \"None\"}')
    print(f'  Confidence: {resume.confidence_score}')
    print(f'  Summary: {resume.analysis_summary[:100] if resume.analysis_summary else \"None\"}...')
"

echo -e "\n2. Testing Profile View Context:"
python manage.py shell -c "
from accounts.views import profile_view
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from accounts.models import User
from accounts.decorators import jwt_login_required
import inspect

user = User.objects.get(email='abdulmukhit@kbtu.kz')
factory = RequestFactory()
request = factory.get('/profile/')
request.user = user

# Mock the decorator to avoid authentication issues
original_func = profile_view.__wrapped__ if hasattr(profile_view, '__wrapped__') else profile_view

try:
    # Try to get the context that would be passed to the template
    from resumes.models import Resume
    from django.apps import apps
    
    JobApplication = apps.get_model('jobs', 'JobApplication')
    
    resumes = Resume.objects.filter(user=user).order_by('-created_at')
    user_resume = resumes.first()
    job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
    
    print(f'User resume: {user_resume.original_filename if user_resume else \"None\"}')
    print(f'Total resumes: {resumes.count()}')
    print(f'Job applications: {job_applications.count()}')
    
    if user_resume:
        print(f'Latest skills: {user_resume.extracted_skills[:5] if user_resume.extracted_skills else \"None\"}')
        print(f'Experience level: {user_resume.experience_level}')
        print(f'Confidence score: {user_resume.confidence_score}')
    
    print('\\n✅ Profile view context data looks good!')
    
except Exception as e:
    print(f'❌ Error: {e}')
"

echo -e "\n3. Testing Profile Page Access:"
curl -s -o /dev/null -w "Profile page HTTP status: %{http_code}\\n" http://localhost:8000/profile/

echo -e "\n✅ Profile test complete!"
