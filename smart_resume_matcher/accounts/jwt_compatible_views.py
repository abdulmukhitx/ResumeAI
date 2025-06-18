"""
JWT-Compatible Views
These views work with JWT authentication and don't require Django sessions.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from resumes.forms import ResumeUploadForm
from resumes.views import analyze_resume
from django.db import transaction
import logging

# Import our custom decorator
from .decorators import jwt_login_required

# Dynamically load models
Resume = apps.get_model('resumes', 'Resume')
JobApplication = apps.get_model('jobs', 'JobApplication')

def jwt_profile_view(request):
    """
    JWT-compatible profile view that doesn't require session authentication.
    Authentication is handled by JavaScript on the frontend.
    """
    # This view doesn't check authentication - it's handled by JavaScript
    # The template will show appropriate content based on JWT token presence
    return render(request, 'accounts/jwt_profile.html')

def jwt_home_view(request):
    """
    JWT-compatible home view that works without session authentication.
    """
    return render(request, 'home.html')

# Keep the original session-based views as fallbacks
@jwt_login_required
def profile_view(request):
    """
    Original session-based profile view (fallback)
    """
    user = request.user
    # Use a safer approach to check profile picture
    try:
        if user.profile_picture and hasattr(user.profile_picture, 'name'):
            import os
            from django.conf import settings
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)):
                user.profile_picture = None
                user.save(update_fields=['profile_picture'])
    except ValueError:
        # If there's any issue with the profile picture, reset it
        user.profile_picture = None
        user.save(update_fields=['profile_picture'])
    
    user_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
    job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
    
    context = {
        'user_resume': user_resume,
        'job_applications': job_applications,
    }
    return render(request, 'accounts/profile.html', context)

def jwt_resume_upload_view(request):
    """
    JWT-compatible resume upload view.
    This view serves the template and lets JavaScript handle authentication.
    No Django authentication required - JWT handled by frontend.
    """
    return render(request, 'resumes/jwt_upload.html')
