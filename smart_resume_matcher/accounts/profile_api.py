"""
Profile API Views
Provides JWT-authenticated API endpoints for user profile data including resume information.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.apps import apps
from django.db import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import json
import logging

logger = logging.getLogger(__name__)

# Dynamically load models
Resume = apps.get_model('resumes', 'Resume')
JobApplication = apps.get_model('jobs', 'JobApplication')

def jwt_authenticate_user(request):
    """
    Authenticate user using JWT token from Authorization header.
    Returns the user object if valid, None otherwise.
    """
    try:
        jwt_auth = JWTAuthentication()
        
        # Try to get the user from the JWT token
        validated_token = jwt_auth.get_validated_token(jwt_auth.get_raw_token(jwt_auth.get_header(request)))
        user = jwt_auth.get_user(validated_token)
        
        return user
    except (InvalidToken, TokenError, Exception) as e:
        logger.debug(f"JWT authentication failed: {e}")
        return None

@csrf_exempt
@require_http_methods(["GET"])
def profile_data_api(request):
    """
    API endpoint to get user profile data including resume information.
    Returns JSON data for authenticated users.
    """
    try:
        # Authenticate user via JWT
        user = jwt_authenticate_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required',
                'authenticated': False
            }, status=401)
        
        # Get user's latest resume
        user_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
        
        # Get user's job applications
        job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
        
        # Prepare resume data
        resume_data = None
        if user_resume:
            resume_data = {
                'id': user_resume.id,
                'filename': user_resume.original_filename,
                'uploaded_at': user_resume.created_at.isoformat() if user_resume.created_at else None,
                'status': user_resume.status,
                'skills': user_resume.extracted_skills if user_resume.extracted_skills else [],
                'experience_level': user_resume.experience_level or 'Not specified',
                'ai_summary': user_resume.analysis_summary or 'Processing...',
                'file_url': user_resume.file.url if user_resume.file else None,
                'confidence_score': user_resume.confidence_score,
                'job_titles': user_resume.job_titles if user_resume.job_titles else [],
                'education': user_resume.education if user_resume.education else [],
                'work_experience': user_resume.work_experience if user_resume.work_experience else [],
            }
        
        # Prepare applications data
        applications_data = []
        for app in job_applications[:10]:  # Limit to recent 10
            applications_data.append({
                'id': app.id,
                'job_title': app.job.title if hasattr(app, 'job') and app.job else 'Unknown',
                'company': getattr(app.job, 'company', 'Unknown') if hasattr(app, 'job') and app.job else 'Unknown',
                'applied_date': app.applied_date.isoformat() if app.applied_date else None,
                'status': getattr(app, 'status', 'applied'),
            })
        
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'resume': resume_data,
            'applications': applications_data,
            'has_resume': resume_data is not None,
        })
        
    except Exception as e:
        logger.error(f"Error in profile_data_api: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
