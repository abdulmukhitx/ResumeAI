from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.apps import apps
from django.utils import timezone
import os
import logging

# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jwt_resume_upload_api(request):
    """
    JWT-authenticated API endpoint for resume upload and analysis.
    Handles file upload, saves to database, and triggers analysis.
    """
    logger.info(f"Resume upload request received from user: {request.user.id}")
    
    try:
        # Check if file was uploaded
        if 'file' not in request.FILES:
            logger.error("No file in request")
            return Response({
                'success': False,
                'error': 'No file uploaded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        logger.info(f"File received: {uploaded_file.name}, size: {uploaded_file.size}")
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            logger.error(f"Invalid file type: {uploaded_file.name}")
            return Response({
                'success': False,
                'error': 'Only PDF files are allowed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (5MB limit)
        if uploaded_file.size > 5 * 1024 * 1024:
            logger.error(f"File too large: {uploaded_file.size} bytes")
            return Response({
                'success': False,
                'error': 'File size exceeds 5MB limit'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deactivate existing resumes for this user
        deactivated_count = Resume.objects.filter(user=request.user, is_active=True).update(is_active=False)
        logger.info(f"Deactivated {deactivated_count} existing resumes")
        
        # Create new resume record
        try:
            resume = Resume.objects.create(
                user=request.user,
                file=uploaded_file,
                original_filename=uploaded_file.name,
                status='pending',
                file_size=uploaded_file.size,
                is_active=True
            )
            logger.info(f"Resume created successfully with ID: {resume.id}")
        except Exception as e:
            logger.error(f"Error creating resume record: {e}")
            return Response({
                'success': False,
                'error': 'Failed to save resume to database'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Resume uploaded successfully for user {request.user.id}: {resume.id}")
        
        # Return success response immediately
        response_data = {
            'success': True,
            'message': 'Resume uploaded successfully',
            'resume': {
                'id': resume.id,
                'filename': resume.original_filename,
                'status': resume.status,
                'uploaded_at': resume.created_at.isoformat(),
                'file_url': resume.file.url if resume.file else None,
            }
        }
        
        # Return success response FIRST - analysis errors should not affect upload success
        logger.info(f"Resume uploaded successfully for user {request.user.id}: {resume.id}")
        upload_response = Response(response_data, status=status.HTTP_201_CREATED)
        
        # Trigger analysis in the background in a separate thread to prevent blocking the response
        import threading
        
        def background_analysis():
            """Run analysis in background thread with modern ASCII-safe processing"""
            try:
                logger.info(f"Starting modern background analysis for resume {resume.id}")
                
                # Import modern processor
                from modern_resume_processor import ModernResumeProcessor
                
                # Get file path
                file_path = resume.file.path
                
                # Initialize modern processor
                processor = ModernResumeProcessor()
                
                # Run modern analysis
                result = processor.process_resume(file_path)
                
                analysis_success = result.success
                
                if analysis_success:
                    logger.info(f"Modern resume analysis completed successfully for resume {resume.id}")
                    
                    # Update resume with modern results
                    try:
                        from django.db import transaction
                        from datetime import datetime
                        import json
                        
                        with transaction.atomic():
                            resume.refresh_from_db()
                            
                            # Store raw text (ASCII-safe, truncated)
                            resume.raw_text = result.extracted_text[:10000] if result.extracted_text else ""
                            
                            # Update skills from analysis
                            resume.extracted_skills = result.skills[:20] if result.skills else []
                            
                            # Update experience level
                            resume.experience_level = result.experience_level or 'Junior'
                            
                            # Store job titles
                            resume.job_titles = getattr(result, 'job_titles', [])[:10] if hasattr(result, 'job_titles') else []
                            
                            # Store education
                            resume.education = getattr(result, 'education', [])[:5] if hasattr(result, 'education') else []
                            
                            # Store work experience
                            resume.work_experience = getattr(result, 'work_experience', [])[:10] if hasattr(result, 'work_experience') else []
                            
                            # Store complete modern analysis
                            combined_analysis = {
                                'extraction_info': {
                                    'text_length': len(result.extracted_text) if result.extracted_text else 0,
                                    'extraction_method': result.extraction_method or 'unknown',
                                    'processing_method': result.processing_method or 'unknown',
                                    'success': result.success,
                                    'ascii_safe': True,
                                    'modern_processor': True
                                },
                                'skills_count': len(result.skills) if result.skills else 0,
                                'resume_score': result.resume_score or 0.0,
                                'processing_metadata': {
                                    'modern_system': True,
                                    'processor_version': 'modern',
                                    'encoding': 'ascii_safe',
                                    'timestamp': datetime.now().isoformat()
                                }
                            }
                            
                            resume.analysis_summary = json.dumps(combined_analysis)
                            
                            # Set confidence score
                            resume.confidence_score = result.confidence_score or 0.0
                            
                            # Update status
                            resume.status = 'completed'
                            resume.analysis_completed_at = datetime.now()
                            
                            resume.save()
                            
                            logger.info(f"Successfully updated resume {resume.id} with modern results")
                    
                    except Exception as update_error:
                        logger.error(f"Error updating resume {resume.id} with modern results: {update_error}")
                        resume.status = 'failed'
                        resume.analysis_summary = f"Modern processing succeeded but update failed: {str(update_error)[:200]}"
                        resume.save(update_fields=['status', 'analysis_summary'])
                else:
                    logger.warning(f"Modern resume analysis failed for resume {resume.id}: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                    resume.status = 'failed'
                    resume.analysis_summary = f"Modern processing failed: {result.error if hasattr(result, 'error') else 'Unknown error'}"[:200]
                    resume.save(update_fields=['status', 'analysis_summary'])
                    
            except ImportError as e:
                logger.error(f"Import error for enhanced_resume_analysis: {e}")
                safe_error_msg = f"Analysis module import failed: {str(e)[:100]}"
                try:
                    resume.refresh_from_db()
                    resume.status = 'failed'
                    resume.analysis_summary = safe_error_msg
                    resume.save(update_fields=['status', 'analysis_summary'])
                except Exception:
                    pass
                    
            except (UnicodeDecodeError, UnicodeError, UnicodeEncodeError) as e:
                logger.error(f"Unicode error during analysis for resume {resume.id}: {e}")
                safe_error_msg = f"Analysis failed due to encoding issues: {type(e).__name__}"
                try:
                    resume.refresh_from_db()
                    resume.status = 'failed'
                    resume.analysis_summary = safe_error_msg
                    resume.save(update_fields=['status', 'analysis_summary'])
                except Exception:
                    pass
                    
            except ValueError as e:
                logger.error(f"Value error during analysis for resume {resume.id}: {e}")
                safe_error_msg = "Analysis failed due to data formatting issues"
                try:
                    resume.refresh_from_db()
                    resume.status = 'failed'
                    resume.analysis_summary = safe_error_msg
                    resume.save(update_fields=['status', 'analysis_summary'])
                except Exception:
                    pass
                    
            except Exception as e:
                logger.error(f"Unexpected error during resume analysis for resume {resume.id}: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                safe_error_msg = f"Analysis failed: {type(e).__name__}"
                try:
                    resume.refresh_from_db()
                    resume.status = 'failed' 
                    resume.analysis_summary = safe_error_msg
                    resume.save(update_fields=['status', 'analysis_summary'])
                except Exception:
                    pass
        
        # Start background analysis thread
        analysis_thread = threading.Thread(target=background_analysis, daemon=True)
        analysis_thread.start()
        
        return upload_response
        
    except Exception as e:
        logger.error(f"Resume upload error for user {request.user.id}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        
        # Try to provide more specific error information
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Sanitize error message to prevent JSON encoding issues
        def sanitize_error_message(error_msg):
            """Clean error message to ensure it's JSON-safe"""
            if not error_msg:
                return 'Unknown error'
            
            try:
                # Convert to string and handle encoding issues
                error_str = str(error_msg)
                # Remove problematic characters
                cleaned = ''.join(char for char in error_str if ord(char) < 128 or char.isalnum() or char.isspace() or char in '.,!?-()[]{}":')
                # Ensure it's valid UTF-8
                cleaned.encode('utf-8').decode('utf-8')
                return cleaned if cleaned.strip() else 'Error occurred during processing'
            except:
                return 'Error occurred during processing'
        
        safe_error_msg = sanitize_error_message(str(e))
        
        return Response({
            'success': False,
            'error': 'Upload failed. Please try again.',
            'debug_info': safe_error_msg
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
