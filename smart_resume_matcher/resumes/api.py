"""
Resume API for handling file uploads and analysis.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.apps import apps
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import json
import logging
import os
import threading

logger = logging.getLogger(__name__)

# Dynamically load models
Resume = apps.get_model('resumes', 'Resume')

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
@require_http_methods(["POST"])
def resume_upload_api(request):
    """
    API endpoint to upload resume files.
    """
    try:
        # Authenticate user via JWT
        user = jwt_authenticate_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required',
                'authenticated': False
            }, status=401)
        
        # Check if file was uploaded
        if 'file' not in request.FILES:
            return JsonResponse({
                'error': 'No file uploaded',
                'message': 'Please select a file to upload'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        original_filename = request.POST.get('original_filename', uploaded_file.name)
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'error': 'Invalid file type',
                'message': 'Only PDF files are allowed'
            }, status=400)
        
        # Validate file size (5MB limit)
        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'error': 'File too large',
                'message': 'File size must be less than 5MB'
            }, status=400)
        
        # Deactivate existing resumes for this user
        Resume.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new resume record
        resume = Resume.objects.create(
            user=user,
            file=uploaded_file,
            original_filename=original_filename,
            file_size=uploaded_file.size,
            status='pending'
        )
        
        # Start background analysis
        start_resume_analysis(resume.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Resume uploaded successfully',
            'resume_id': resume.id,
            'filename': original_filename,
            'status': 'pending'
        })
        
    except Exception as e:
        logger.error(f"Error in resume_upload_api: {e}")
        return JsonResponse({
            'error': 'Upload failed',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def resume_status_api(request, resume_id):
    """
    API endpoint to check resume analysis status.
    """
    try:
        # Authenticate user via JWT
        user = jwt_authenticate_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        # Get resume
        try:
            resume = Resume.objects.get(id=resume_id, user=user)
        except Resume.DoesNotExist:
            return JsonResponse({
                'error': 'Resume not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'resume_id': resume.id,
            'status': resume.status,
            'filename': resume.original_filename,
            'uploaded_at': resume.created_at.isoformat() if resume.created_at else None,
            'analysis_started_at': resume.analysis_started_at.isoformat() if resume.analysis_started_at else None,
            'analysis_completed_at': resume.analysis_completed_at.isoformat() if resume.analysis_completed_at else None,
            'skills_count': len(resume.extracted_skills) if resume.extracted_skills else 0,
            'has_summary': bool(resume.analysis_summary),
        })
        
    except Exception as e:
        logger.error(f"Error in resume_status_api: {e}")
        return JsonResponse({
            'error': 'Status check failed',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def resume_list_api(request):
    """
    API endpoint to list user's resumes.
    """
    try:
        # Authenticate user via JWT
        user = jwt_authenticate_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        # Get user's resumes
        resumes = Resume.objects.filter(user=user).order_by('-created_at')
        
        resume_list = []
        for resume in resumes:
            resume_list.append({
                'id': resume.id,
                'filename': resume.original_filename,
                'status': resume.status,
                'uploaded_at': resume.created_at.isoformat() if resume.created_at else None,
                'is_active': resume.is_active,
                'file_size': resume.file_size,
                'skills_count': len(resume.extracted_skills) if resume.extracted_skills else 0,
            })
        
        return JsonResponse({
            'success': True,
            'resumes': resume_list,
            'count': len(resume_list)
        })
        
    except Exception as e:
        logger.error(f"Error in resume_list_api: {e}")
        return JsonResponse({
            'error': 'List retrieval failed',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def resume_analysis_api(request, resume_id):
    """
    API endpoint to get detailed resume analysis results.
    """
    try:
        # Authenticate user via JWT
        user = jwt_authenticate_user(request)
        if not user:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        # Get resume
        try:
            resume = Resume.objects.get(id=resume_id, user=user)
        except Resume.DoesNotExist:
            return JsonResponse({
                'error': 'Resume not found'
            }, status=404)
        
        # Parse analysis results
        analysis_data = {}
        if resume.analysis_summary:
            try:
                if isinstance(resume.analysis_summary, str):
                    analysis_data = json.loads(resume.analysis_summary)
                else:
                    analysis_data = resume.analysis_summary
            except json.JSONDecodeError:
                # Fallback for old format
                analysis_data = {
                    'extracted_skills': resume.extracted_skills or [],
                    'experience_level': resume.experience_level or 'unknown',
                    'confidence_score': resume.confidence_score or 0.0
                }
        
        return JsonResponse({
            'success': True,
            'resume_id': resume.id,
            'status': resume.status,
            'filename': resume.original_filename,
            'analysis': analysis_data,
            'extracted_skills': resume.extracted_skills or [],
            'experience_level': resume.experience_level or 'unknown',
            'confidence_score': resume.confidence_score or 0.0,
            'analysis_completed_at': resume.analysis_completed_at.isoformat() if resume.analysis_completed_at else None,
        })
        
    except Exception as e:
        logger.error(f"Error in resume_analysis_api: {e}")
        return JsonResponse({
            'error': 'Analysis retrieval failed',
            'message': str(e)
        }, status=500)

def start_resume_analysis(resume_id):
    """
    Start resume analysis in a background thread.
    """
    def analyze_in_background():
        try:
            from resumes.views import analyze_resume
            analyze_resume(resume_id)
            logger.info(f"Resume analysis completed for ID: {resume_id}")
        except Exception as e:
            logger.error(f"Resume analysis failed for ID {resume_id}: {e}")
    
    # Start analysis in background thread
    thread = threading.Thread(target=analyze_in_background)
    thread.daemon = True
    thread.start()
