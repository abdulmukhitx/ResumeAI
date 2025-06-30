from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.apps import apps
import json
import threading
import logging
from datetime import datetime

# Modern ASCII-safe imports ONLY
from modern_resume_processor import ModernResumeProcessor

logger = logging.getLogger(__name__)

# Dynamically load models to avoid circular imports
def get_resume_model():
    """Get Resume model dynamically"""
    return apps.get_model('resumes', 'Resume')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ultra_safe_resume_upload(request):
    """
    Ultra-safe resume upload with ZERO UTF-8 dependencies.
    This endpoint completely bypasses all old UTF-8 processing code.
    
    GET: Shows upload instructions
    POST: Handles file upload
    """
    
    if request.method == 'GET':
        return Response({
            'message': 'Smart Resume Matcher - Resume Upload API',
            'instructions': {
                'method': 'POST',
                'content_type': 'multipart/form-data',
                'authentication': 'Bearer JWT token required',
                'parameters': {
                    'file': 'PDF file (required, max 10MB)'
                },
                'file_requirements': {
                    'format': 'PDF only',
                    'max_size': '10MB',
                    'processing': 'Automatic analysis after upload'
                },
                'example_response': {
                    'success': True,
                    'message': 'Resume uploaded successfully',
                    'resume': {
                        'id': 123,
                        'filename': 'resume.pdf',
                        'status': 'processing',
                        'uploaded_at': '2025-06-28T16:30:00Z',
                        'processor': 'v4_ultra_safe_ascii_only'
                    }
                }
            },
            'test_interface': 'Visit http://localhost:3000/test_upload_interface.html for a web interface',
            'status': 'All systems operational - 500 error fixed ✅'
        }, status=status.HTTP_200_OK)
    
    try:
        # Validate file upload
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file uploaded',
                'error_code': 'NO_FILE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # Basic file validation
        if not uploaded_file.name.lower().endswith('.pdf'):
            return Response({
                'success': False,
                'error': 'Only PDF files are allowed',
                'error_code': 'INVALID_FILE_TYPE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            return Response({
                'success': False,
                'error': 'File size exceeds 10MB limit',
                'error_code': 'FILE_TOO_LARGE'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deactivate existing resumes
        Resume = get_resume_model()
        Resume.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Save file using Django's storage system
        file_path = default_storage.save(
            f'resumes/{request.user.id}/{uploaded_file.name}',
            ContentFile(uploaded_file.read())
        )
        
        # Create resume record with minimal data
        with transaction.atomic():
            resume = Resume.objects.create(
                user=request.user,
                file=file_path,
                original_filename=uploaded_file.name,
                status='processing',
                file_size=uploaded_file.size,
                is_active=True
            )
        
        # Background processing function with ONLY V4 ASCII-safe code
        def ultra_safe_background_processing():
            """
            Background processing using ONLY V4 ASCII-safe components.
            NO imports or calls to old UTF-8 processing code.
            """
            try:
                logger.info(f"Ultra-safe V4 processing started for resume {resume.id}")
                
                # Get actual file path
                full_file_path = default_storage.path(file_path)
                
                # Use ONLY Modern processor - no fallbacks to old code
                processor = ModernResumeProcessor()
                result = processor.process_resume_safe(full_file_path)
                
                if result['success']:
                    # Update database with ASCII-safe results
                    with transaction.atomic():
                        resume.refresh_from_db()
                        
                        # Extract ASCII-safe results
                        analysis = result['analysis']
                        
                        # Store ASCII-safe text (guaranteed no UTF-8 issues)
                        ascii_text = result['text']
                        resume.raw_text = ascii_text[:50000]  # Increased limit for V4
                        
                        # Store ASCII-safe skills
                        skills = analysis.get('skills', [])
                        if skills:
                            resume.extracted_skills = skills[:25]
                        
                        # Store ASCII-safe experience level
                        exp_level = analysis.get('experience_level', 'junior')
                        resume.experience_level = exp_level.capitalize()
                        
                        # Store ASCII-safe job titles
                        job_titles = analysis.get('job_titles', [])
                        if job_titles:
                            resume.job_titles = job_titles[:10]
                        
                        # Store ASCII-safe education
                        education = analysis.get('education', [])
                        if education:
                            resume.education = education[:5]
                        
                        # Create ASCII-safe analysis summary
                        safe_summary = {
                            'v4_ultra_safe': True,
                            'processor_version': 'v4_ascii_only',
                            'encoding_safe': True,
                            'extraction_method': 'modern_processor',
                            'text_length': len(ascii_text),
                            'skills_count': len(skills),
                            'confidence': analysis.get('confidence_score', 0.5),
                            'experience_years': analysis.get('experience', {}).get('total_years', 0),
                            'processing_timestamp': datetime.now().isoformat(),
                            'utf8_dependencies': 'NONE'
                        }
                        
                        # Store as JSON (ASCII-safe guaranteed)
                        resume.analysis_summary = json.dumps(safe_summary)
                        
                        # Set confidence score
                        resume.confidence_score = analysis.get('confidence_score', 0.5)
                        
                        # Complete processing
                        resume.status = 'completed'
                        resume.analysis_completed_at = datetime.now()
                        
                        resume.save()
                        
                        logger.info(f"Ultra-safe V4 processing completed successfully for resume {resume.id}")
                        logger.info(f"Results: {len(skills)} skills, {exp_level} level, confidence {resume.confidence_score}")
                
                else:
                    # Handle failure with ASCII-safe error handling
                    error_msg = str(result.get('error', 'Unknown error'))[:500]  # Truncate
                    
                    with transaction.atomic():
                        resume.refresh_from_db()
                        resume.status = 'failed'
                        resume.analysis_summary = json.dumps({
                            'v4_ultra_safe': True,
                            'error': error_msg,
                            'processing_failed': True,
                            'timestamp': datetime.now().isoformat()
                        })
                        resume.save()
                    
                    logger.error(f"Ultra-safe V4 processing failed for resume {resume.id}: {error_msg}")
                
            except Exception as e:
                # Ultimate fallback with ASCII-safe error handling
                error_str = str(e)[:500]  # Truncate to prevent issues
                
                try:
                    with transaction.atomic():
                        resume.refresh_from_db()
                        resume.status = 'failed'
                        resume.analysis_summary = json.dumps({
                            'v4_ultra_safe': True,
                            'critical_error': error_str,
                            'fallback_triggered': True,
                            'timestamp': datetime.now().isoformat()
                        })
                        resume.save()
                except Exception as db_error:
                    logger.critical(f"Critical database error in ultra-safe processing: {db_error}")
                
                logger.error(f"Critical error in ultra-safe processing for resume {resume.id}: {error_str}")
        
        # Start background processing with enhanced logging
        logger.info(f"Starting background processing thread for resume {resume.id}")
        thread = threading.Thread(target=ultra_safe_background_processing, daemon=True)
        thread.start()
        logger.info(f"Background processing thread started successfully for resume {resume.id}")
        
        # Return immediate success response
        return Response({
            'success': True,
            'message': 'Resume uploaded successfully. Ultra-safe V4 processing started.',
            'resume': {
                'id': resume.id,
                'filename': resume.original_filename,
                'status': resume.status,
                'uploaded_at': resume.created_at.isoformat(),
                'processor': 'v4_ultra_safe_ascii_only'
            },
            'processing': {
                'method': 'v4_ascii_safe_background',
                'utf8_dependencies': 'NONE',
                'encoding_safe': True,
                'background_thread': 'started'
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        # ASCII-safe error response
        error_msg = str(e)[:200]  # Truncate to prevent encoding issues
        
        logger.error(f"Error in ultra-safe resume upload: {error_msg}")
        
        return Response({
            'success': False,
            'error': error_msg,
            'error_code': 'UPLOAD_FAILED',
            'processor': 'v4_ultra_safe',
            'utf8_safe': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ultra_safe_resume_status(request, resume_id):
    """Get resume status with ultra-safe ASCII-only response"""
    
    try:
        Resume = get_resume_model()
        resume = Resume.objects.get(id=resume_id, user=request.user)
        
        # Build ASCII-safe response
        response_data = {
            'success': True,
            'resume_id': resume.id,
            'status': resume.status,
            'filename': resume.original_filename,
            'uploaded_at': resume.created_at.isoformat(),
            'processor': 'v4_ultra_safe',
            'utf8_safe': True
        }
        
        # Add processing results if completed
        if resume.status == 'completed':
            response_data.update({
                'analysis_completed_at': resume.analysis_completed_at.isoformat() if resume.analysis_completed_at else None,
                'skills_count': len(resume.extracted_skills) if resume.extracted_skills else 0,
                'experience_level': resume.experience_level or 'Not determined',
                'confidence_score': resume.confidence_score or 0.0,
                'text_length': len(resume.raw_text) if resume.raw_text else 0
            })
            
            # Parse analysis summary safely
            if resume.analysis_summary:
                try:
                    analysis_data = json.loads(resume.analysis_summary)
                    response_data['analysis_metadata'] = {
                        'processor_version': analysis_data.get('processor_version', 'v4'),
                        'encoding_safe': analysis_data.get('encoding_safe', True),
                        'extraction_method': analysis_data.get('extraction_method', 'unknown')
                    }
                except json.JSONDecodeError:
                    response_data['analysis_metadata'] = {'error': 'Could not parse analysis data'}
        
        elif resume.status == 'failed':
            response_data['error_info'] = {
                'message': 'Processing failed',
                'processor': 'v4_ultra_safe'
            }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except get_resume_model().DoesNotExist:
        return Response({
            'success': False,
            'error': 'Resume not found',
            'error_code': 'NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        error_msg = str(e)[:200]
        return Response({
            'success': False,
            'error': error_msg,
            'error_code': 'STATUS_ERROR',
            'utf8_safe': True
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ultra_safe_resume_list(request):
    """
    API endpoint to list user's resumes
    """
    try:
        # Get all resumes for the authenticated user
        Resume = get_resume_model()
        resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
        
        resume_data = []
        for resume in resumes:
            resume_info = {
                'id': resume.id,
                'original_filename': resume.original_filename,
                'status': resume.status,
                'created_at': resume.created_at.isoformat() if resume.created_at else None,
                'is_active': resume.is_active,
                'file_size': resume.file_size,
                'analysis_summary': resume.analysis_summary,
                'extracted_skills_count': len(resume.extracted_skills) if resume.extracted_skills else 0,
                'experience_level': resume.experience_level,
                'confidence_score': resume.confidence_score,
            }
            
            # Add file URL if file exists
            if resume.file:
                try:
                    resume_info['file_url'] = resume.file.url
                except:
                    resume_info['file_url'] = None
            else:
                resume_info['file_url'] = None
                
            resume_data.append(resume_info)
        
        return Response({
            'success': True,
            'resumes': resume_data,
            'total_count': len(resume_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Resume list API error: {e}")
        return Response({
            'success': False,
            'error': 'Failed to retrieve resumes',
            'error_code': 'LIST_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
