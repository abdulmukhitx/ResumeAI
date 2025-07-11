"""
JWT-Protected API Views for Smart Resume Matcher
These views replace the session-based views and work exclusively with JWT authentication.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import logging
import re

logger = logging.getLogger(__name__)

# Dynamically load models
User = get_user_model()
Resume = apps.get_model('resumes', 'Resume')
JobApplication = apps.get_model('jobs', 'JobApplication')
JobMatch = apps.get_model('jobs', 'JobMatch')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_api_view(request):
    """
    JWT-protected profile data API endpoint
    """
    try:
        user = request.user
        
        # Get user resume
        user_resume = Resume.objects.filter(user=user, is_active=True).first()
        
        # Get job applications
        job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')[:10]
        
        # Prepare user data
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': getattr(user, 'phone', ''),
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'profile_picture_url': user.get_profile_picture_url() if hasattr(user, 'get_profile_picture_url') else None,
        }
        
        # Prepare resume data
        resume_data = None
        if user_resume:
            resume_data = {
                'id': user_resume.id,
                'original_filename': user_resume.original_filename,
                'status': user_resume.status,
                'created_at': user_resume.created_at.isoformat(),
                'extracted_skills': user_resume.extracted_skills or [],
                'experience_level': user_resume.experience_level,
                'analysis_summary': user_resume.analysis_summary,
                'file_url': user_resume.file.url if user_resume.file else None,
            }
        
        # Prepare applications data
        applications_data = []
        for app in job_applications:
            applications_data.append({
                'id': app.id,
                'job_title': app.job.title,
                'company_name': app.job.company_name,
                'match_score': app.match_score,
                'applied_date': app.applied_date.isoformat(),
                'status': app.status,
                'job_id': app.job.id,
            })
        
        return Response({
            'success': True,
            'user': user_data,
            'resume': resume_data,
            'job_applications': applications_data,
        })
        
    except Exception as e:
        logger.error(f"Profile API error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to load profile data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api_view(request):
    """
    JWT-protected dashboard data API endpoint
    """
    try:
        user = request.user
        
        # Get user resume
        user_resume = Resume.objects.filter(user=user, is_active=True).first()
        
        if not user_resume:
            return Response({
                'success': True,
                'has_resume': False,
                'message': 'Please upload your resume to access dashboard features.'
            })
        
        # Get recent job matches
        job_matches = JobMatch.objects.filter(
            resume=user_resume,
            match_score__gte=50
        ).select_related('job').order_by('-match_score')[:6]
        
        # Prepare job matches data
        matches_data = []
        for match in job_matches:
            matches_data.append({
                'id': match.job.id,
                'title': match.job.title,
                'company': match.job.company_name,
                'location': match.job.location,
                'match_score': match.match_score,
                'description': match.job.description[:200] + '...' if len(match.job.description) > 200 else match.job.description,
                'published_at': match.job.published_at.isoformat() if match.job.published_at else None,
            })
        
        return Response({
            'success': True,
            'has_resume': True,
            'resume': {
                'id': user_resume.id,
                'status': user_resume.status,
                'skills_count': len(user_resume.extracted_skills or []),
            },
            'job_matches': matches_data,
            'total_matches': len(matches_data),
        })
        
    except Exception as e:
        logger.error(f"Dashboard API error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to load dashboard data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_api_view(request):
    """
    Simple API to get current user info for navigation
    """
    try:
        user = request.user
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.email,
            }
        })
    except Exception as e:
        logger.error(f"User info API error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to get user info'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # No authentication required for registration
def register_api_view(request):
    """
    API endpoint for user registration
    """
    try:
        # Get form data
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        password_confirm = request.data.get('password_confirm', '')
        
        # Validation
        errors = {}
        
        if not first_name:
            errors['first_name'] = ['First name is required']
        elif len(first_name) < 2:
            errors['first_name'] = ['First name must be at least 2 characters']
            
        if not last_name:
            errors['last_name'] = ['Last name is required']
        elif len(last_name) < 2:
            errors['last_name'] = ['Last name must be at least 2 characters']
            
        if not email:
            errors['email'] = ['Email is required']
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors['email'] = ['Please enter a valid email address']
        elif User.objects.filter(email=email).exists():
            errors['email'] = ['An account with this email already exists']
            
        if not password:
            errors['password'] = ['Password is required']
        elif len(password) < 8:
            errors['password'] = ['Password must be at least 8 characters long']
            
        if not password_confirm:
            errors['password_confirm'] = ['Please confirm your password']
        elif password != password_confirm:
            errors['password_confirm'] = ['Passwords do not match']
            
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            
        # Create user
        try:
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            return Response({
                'message': 'Account created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError:
            return Response({
                'email': ['An account with this email already exists']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': f'Registration failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
