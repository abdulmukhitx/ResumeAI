# filepath: /home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/resumes/api_views_v3.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from .models import Resume
import json
import threading
import logging
from datetime import datetime

# V4 ASCII-safe imports
from pdf_processor_v4 import PDFProcessorV4
from ai_analyzer_v4 import AIAnalyzerV4
from resume_processor_v4 import ResumeProcessorV4

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_resume_v3(request):
    """Enhanced resume upload using V4 ASCII-safe processors"""
    
    try:
        # Get uploaded file
        if 'resume_file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No resume file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resume_file = request.FILES['resume_file']
        
        # Validate file
        if not resume_file.name.lower().endswith('.pdf'):
            return Response({
                'success': False,
                'error': 'Only PDF files are supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if resume_file.size > 10 * 1024 * 1024:  # 10MB limit
            return Response({
                'success': False,
                'error': 'File too large. Maximum size is 10MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save file to storage
        file_path = default_storage.save(
            f'resumes/{request.user.id}/{resume_file.name}',
            ContentFile(resume_file.read())
        )
        
        full_file_path = default_storage.path(file_path)
        
        # Create resume record
        with transaction.atomic():
            resume = Resume.objects.create(
                user=request.user,
                file=file_path,
                original_filename=resume_file.name,
                status='processing'
            )
        
        # Start background processing with V4 ASCII-safe system
        def process_resume_background():
            try:
                logger.info(f"Starting V4 ASCII-safe processing for resume {resume.id}")
                
                # Initialize V4 processor (ASCII-safe)
                resume_processor = ResumeProcessorV4()
                
                # Process resume with ASCII-safe handling
                result = resume_processor.process_resume(full_file_path)
                
                if not result['success']:
                    raise Exception(f"V4 resume processing failed: {result.get('error')}")
                
                logger.info(f"V4 processing successful: {len(result['extraction']['text'])} characters using {result['extraction'].get('method')}")
                
                # Extract analysis results
                analysis = result['analysis']
                extraction = result['extraction']
                
                # Update resume record with V4 ASCII-safe results
                with transaction.atomic():
                    resume.refresh_from_db()
                    
                    # Store raw text (ASCII-safe, truncated to 10k chars)
                    resume.raw_text = extraction['text'][:10000]
                    
                    # Update skills from analysis
                    if analysis.get('skills') and analysis['skills'].get('technical'):
                        resume.extracted_skills = analysis['skills']['technical'][:20]  # Limit to 20 skills
                    
                    # Update experience level
                    experience_years = 0
                    if analysis.get('experience') and analysis['experience'].get('total_years'):
                        experience_years = analysis['experience']['total_years']
                    
                    if experience_years >= 5:
                        resume.experience_level = 'Senior'
                    elif experience_years >= 2:
                        resume.experience_level = 'Mid-level'
                    else:
                        resume.experience_level = 'Junior'
                    
                    # Store complete V4 analysis
                    combined_analysis = {
                        'extraction_info': {
                            'text_length': len(extraction['text']),
                            'method_used': extraction.get('method'),
                            'success': extraction['success'],
                            'pages': extraction.get('metadata', {}).get('pages', 0),
                            'ascii_safe': True
                        },
                        'analysis': analysis,
                        'processing_metadata': {
                            'v4_ascii_safe_system': True,
                            'processor_version': 'v4',
                            'encoding': 'ascii_only',
                            'timestamp': datetime.now().isoformat(),
                            'provider_used': result.get('provider_used', 'unknown')
                        }
                    }
                    
                    resume.analysis_summary = json.dumps(combined_analysis)
                    
                    # Set confidence score
                    confidence = analysis.get('overall_score', 50) / 100.0
                    resume.confidence_score = confidence
                    
                    # Update status
                    resume.status = 'completed'
                    resume.analysis_completed_at = datetime.now()
                    
                    resume.save()
                    
                    logger.info(f"Successfully processed resume {resume.id} with V4 ASCII-safe system - confidence: {confidence:.2f}")
                    
            except Exception as e:
                logger.error(f"Error processing resume {resume.id} with V4 system: {str(e)}")
                
                # Fallback to simple ASCII-safe processing
                try:
                    logger.info(f"Attempting ASCII-safe fallback for resume {resume.id}")
                    
                    # Initialize V4 components for fallback
                    pdf_processor = PDFProcessorV4()
                    ai_analyzer = AIAnalyzerV4()
                    
                    # Try basic text extraction
                    extraction_result = pdf_processor.extract_text_ascii_safe(full_file_path)
                    
                    if extraction_result['success'] and extraction_result['text']:
                        # Try local analysis with ASCII-safe text
                        analysis_result = ai_analyzer._analyze_locally_ascii_safe(extraction_result['text'])
                        
                        with transaction.atomic():
                            resume.refresh_from_db()
                            
                            # Update with fallback analysis
                            if analysis_result.get('skills') and analysis_result['skills'].get('technical'):
                                resume.extracted_skills = analysis_result['skills']['technical'][:10]
                            
                            # Set basic experience level
                            exp_years = analysis_result.get('experience', {}).get('total_years', 0)
                            if exp_years >= 3:
                                resume.experience_level = 'Mid-level'
                            elif exp_years > 0:
                                resume.experience_level = 'Junior'
                            else:
                                resume.experience_level = 'Entry-level'
                            
                            # Store fallback analysis
                            fallback_analysis = {
                                'fallback_used': True,
                                'v4_ascii_safe_fallback': True,
                                'extraction_info': {
                                    'text_length': len(extraction_result['text']),
                                    'method_used': extraction_result.get('method'),
                                    'success': extraction_result['success'],
                                    'ascii_safe': True
                                },
                                'analysis': analysis_result,
                                'error_details': str(e),
                                'processing_metadata': {
                                    'fallback_processor': 'v4_ascii_safe',
                                    'timestamp': datetime.now().isoformat()
                                }
                            }
                            
                            resume.analysis_summary = json.dumps(fallback_analysis)
                            
                            # Set confidence score
                            confidence = analysis_result.get('overall_score', 30) / 100.0
                            resume.confidence_score = confidence
                            
                            resume.status = 'completed'
                            resume.analysis_completed_at = datetime.now()
                            resume.raw_text = extraction_result['text'][:10000]
                            
                            resume.save()
                            
                            logger.info(f"Successfully processed resume {resume.id} with V4 ASCII-safe fallback")
                    else:
                        raise Exception(f"ASCII-safe fallback extraction failed: {extraction_result.get('error')}")
                        
                except Exception as fallback_error:
                    logger.error(f"V4 ASCII-safe fallback processing also failed for resume {resume.id}: {str(fallback_error)}")
                    
                    with transaction.atomic():
                        resume.refresh_from_db()
                        resume.status = 'failed'
                        resume.analysis_summary = json.dumps({
                            'error': 'All processing methods failed',
                            'primary_error': str(e),
                            'fallback_error': str(fallback_error),
                            'v4_ascii_safe_attempted': True,
                            'timestamp': datetime.now().isoformat()
                        })
                        resume.save()
        
        # Start background thread
        thread = threading.Thread(target=process_resume_background, daemon=True)
        thread.start()
        
        return Response({
            'success': True,
            'message': 'Resume uploaded successfully and processing started with V4 ASCII-safe system',
            'resume_id': resume.id,
            'status': 'processing',
            'file_path': file_path,
            'processor_version': 'v4_ascii_safe'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in upload_resume_v3: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resume_status_v3(request, resume_id):
    """Get processing status of a resume with V4 ASCII-safe results"""
    
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        
        response_data = {
            'resume_id': resume.id,
            'status': resume.status,
            'original_filename': resume.original_filename,
            'created_at': resume.created_at.isoformat(),
            'analyzed_at': resume.analysis_completed_at.isoformat() if resume.analysis_completed_at else None,
            'overall_score': getattr(resume, 'overall_score', resume.confidence_score),
            'confidence_score': resume.confidence_score,
            'experience_level': getattr(resume, 'experience_level', 'Unknown'),
            'processor_version': 'v4_ascii_safe'
        }
        
        # Add detailed analysis if available
        if resume.analysis_summary:
            try:
                analysis_data = json.loads(resume.analysis_summary)
                response_data['detailed_analysis'] = analysis_data
                
                # Check if V4 processing was used
                if analysis_data.get('processing_metadata', {}).get('v4_ascii_safe_system'):
                    response_data['processing_notes'] = 'Processed with V4 ASCII-safe system'
                elif analysis_data.get('v4_ascii_safe_fallback'):
                    response_data['processing_notes'] = 'Processed with V4 ASCII-safe fallback'
                    
            except json.JSONDecodeError:
                response_data['analysis_error'] = 'Could not parse analysis data'
        
        # Add candidate info from analysis if available
        if resume.status == 'completed':
            candidate_info = {
                'name': 'Not extracted',
                'email': 'Not extracted', 
                'phone': 'Not extracted',
                'skills': resume.extracted_skills if resume.extracted_skills else [],
                'years_of_experience': 0
            }
            
            # Try to extract from V4 analysis_summary
            if resume.analysis_summary:
                try:
                    analysis_data = json.loads(resume.analysis_summary)
                    analysis = analysis_data.get('analysis', {})
                    
                    # Extract candidate info
                    if 'candidate_info' in analysis:
                        stored_candidate_info = analysis['candidate_info']
                        candidate_info.update({
                            'name': stored_candidate_info.get('name', 'Not extracted'),
                            'email': stored_candidate_info.get('email', 'Not extracted'),
                            'phone': stored_candidate_info.get('phone', 'Not extracted')
                        })
                    
                    # Extract experience years
                    if 'experience' in analysis:
                        experience = analysis['experience']
                        candidate_info['years_of_experience'] = experience.get('total_years', 0)
                        
                    # Add skills summary
                    if 'skills' in analysis:
                        skills_data = analysis['skills']
                        candidate_info['technical_skills'] = skills_data.get('technical', [])
                        candidate_info['programming_languages'] = skills_data.get('programming_languages', [])
                        candidate_info['tools_technologies'] = skills_data.get('tools_technologies', [])
                        
                except json.JSONDecodeError:
                    pass
            
            response_data['candidate_info'] = candidate_info
        
        # Add error information for failed processing
        if resume.status == 'failed':
            if resume.analysis_summary:
                try:
                    error_data = json.loads(resume.analysis_summary)
                    response_data['error_details'] = error_data
                except json.JSONDecodeError:
                    response_data['error_message'] = resume.analysis_summary
        
        return Response(response_data)
        
    except Resume.DoesNotExist:
        return Response({
            'error': 'Resume not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in get_resume_status_v3: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_resumes_v3(request):
    """List all user resumes with V4 processing status"""
    
    try:
        resumes = Resume.objects.filter(user=request.user).order_by('-created_at')
        
        resume_list = []
        for resume in resumes:
            resume_data = {
                'id': resume.id,
                'original_filename': resume.original_filename,
                'status': resume.status,
                'created_at': resume.created_at.isoformat(),
                'analyzed_at': resume.analysis_completed_at.isoformat() if resume.analysis_completed_at else None,
                'confidence_score': resume.confidence_score,
                'experience_level': getattr(resume, 'experience_level', 'Unknown'),
                'skills_count': len(resume.extracted_skills) if resume.extracted_skills else 0,
                'processor_version': 'v4_ascii_safe'
            }
            
            # Add processing status info
            if resume.analysis_summary:
                try:
                    analysis_data = json.loads(resume.analysis_summary)
                    if analysis_data.get('processing_metadata', {}).get('v4_ascii_safe_system'):
                        resume_data['processing_method'] = 'V4 ASCII-safe'
                    elif analysis_data.get('v4_ascii_safe_fallback'):
                        resume_data['processing_method'] = 'V4 ASCII-safe fallback'
                    else:
                        resume_data['processing_method'] = 'Legacy'
                except:
                    resume_data['processing_method'] = 'Unknown'
            
            resume_list.append(resume_data)
        
        return Response({
            'success': True,
            'resumes': resume_list,
            'total_count': len(resume_list)
        })
        
    except Exception as e:
        logger.error(f"Error in list_resumes_v3: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_resume_v3(request, resume_id):
    """Delete a resume"""
    
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        
        # Delete the file from storage
        if resume.file:
            try:
                default_storage.delete(resume.file.name)
            except:
                pass  # File might not exist
        
        # Delete the database record
        resume.delete()
        
        return Response({
            'success': True,
            'message': 'Resume deleted successfully'
        })
        
    except Resume.DoesNotExist:
        return Response({
            'error': 'Resume not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in delete_resume_v3: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
