from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.apps import apps
from .forms import ResumeUploadForm
from .enhanced_analyzer import AdvancedAIAnalyzer
from .enhanced_job_matcher import AdvancedJobMatcher

# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
Job = apps.get_model('jobs', 'Job')

def resume_upload_view(request):
    """
    Legacy resume upload view - redirects to JWT-compatible version
    This prevents infinite redirect loops by immediately redirecting to JWT URL
    """
    return redirect('/jwt-resume-upload/')

def analyze_resume(resume_id):
    """
    Analyze the resume using AI.
    In a production app, this would be a Celery task.
    """
    import logging
    from django.db import transaction
    logger = logging.getLogger(__name__)
    
    try:
        with transaction.atomic():
            resume = Resume.objects.select_for_update().get(id=resume_id)
            resume.status = 'processing'
            resume.analysis_started_at = timezone.now()
            resume.save()
    except Resume.DoesNotExist:
        logger.error(f"Resume with ID {resume_id} not found")
        return False
    
    try:
        # Initialize Enhanced AI analyzer
        analyzer = AdvancedAIAnalyzer()
        
        # Extract text from PDF
        try:
            resume.raw_text = analyzer.extract_text_from_pdf(resume.file.path)
            
            # Check if extraction failed
            if resume.raw_text.startswith(("PDF_EXTRACTION_FAILED:", "PDF_EXTRACTION_ERROR:", "PDF_EXTRACTION_WARNING:")):
                logger.warning(f"PDF extraction issue for resume {resume_id}: {resume.raw_text[:100]}...")
                # Still proceed with analysis, but mark the issue
                resume.has_extraction_issues = True
            else:
                resume.has_extraction_issues = False
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # If PDF extraction fails, set a descriptive error message
            resume.raw_text = f"PDF_EXTRACTION_ERROR: Failed to extract text from PDF. Error: {str(e)}"
            resume.has_extraction_issues = True
        
        # Save the raw text first
        resume.save(update_fields=['raw_text', 'has_extraction_issues'])
            
        # Analyze the resume using the enhanced analyzer
        analysis_results = analyzer.analyze_resume(resume.raw_text)
        
        # Update resume with enhanced analysis results in a single transaction
        with transaction.atomic():
            resume.refresh_from_db()
            
            # Check if analysis detected errors
            if analysis_results.get('error', False):
                logger.warning(f"Analysis failed for resume {resume_id}: {analysis_results.get('error_message', 'Unknown error')}")
                resume.status = 'failed'
                resume.error_message = analysis_results.get('error_message', 'Analysis failed')
                resume.error_type = analysis_results.get('error_type', 'analysis_error')
                resume.suggestions = analysis_results.get('suggestions', [])
                resume.analysis_completed_at = timezone.now()
                resume.save()
                return False
            
            # Store the new enhanced analysis format
            resume.extracted_skills = analysis_results.get('extracted_skills', [])
            resume.experience_level = analysis_results.get('experience_level', '')
            resume.job_titles = analysis_results.get('job_titles', [])
            resume.education = analysis_results.get('education', [])
            resume.work_experience = analysis_results.get('work_experience', [])
            
            # Store the full enhanced analysis as JSON for the profile page
            import json
            resume.analysis_summary = json.dumps(analysis_results) if isinstance(analysis_results, dict) else analysis_results
            resume.confidence_score = analysis_results.get('confidence_score', 0.0)
            
            # Update status based on extraction issues
            if resume.has_extraction_issues:
                resume.status = 'completed_with_warnings'
                resume.warning_message = "Resume analysis completed, but some text may not have been extracted properly from the PDF."
            else:
                resume.status = 'completed'
                
            resume.analysis_completed_at = timezone.now()
            resume.save()
        
        # Find matching jobs using enhanced matcher
        try:
            find_matching_jobs(resume)
        except Exception as e:
            logger.error(f"Error finding matching jobs: {e}")
            # Don't fail the whole process if job matching fails
        
        return True
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        with transaction.atomic():
            resume.refresh_from_db()
            resume.status = 'failed'
            resume.save()
        raise e

def find_matching_jobs(resume):
    """
    Find jobs matching the resume.
    In a production app, this would be a Celery task.
    """
    import logging
    from jobs.job_matcher import JobMatcher
    from django.db import transaction
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get active jobs
        active_jobs = Job.objects.filter(is_active=True)
        
        if not active_jobs.exists():
            logger.info("No active jobs found in database")
            return
        
        # Initialize job matcher with user and resume
        matcher = JobMatcher(user=resume.user, resume=resume)
        
        # Dynamically import JobMatch model to avoid circular imports
        JobMatch = apps.get_model('jobs', 'JobMatch')
        
        # Match jobs
        matches_created = 0
        for job in active_jobs:
            try:
                # Prepare job data in the format expected by JobMatcher
                job_data = {
                    'name': job.title,
                    'snippet': {
                        'requirement': job.requirements or '',
                        'responsibility': job.responsibilities or ''
                    },
                    'description': job.description,
                    'employer': {
                        'name': job.company_name
                    },
                    'salary': {
                        'from': job.salary_from,
                        'to': job.salary_to,
                        'currency': job.salary_currency
                    },
                    'area': {
                        'name': job.location
                    },
                    'experience': {
                        'name': job.experience_required or ''
                    }
                }
                
                # Calculate match score using the JobMatcher
                match_score, match_details = matcher.calculate_match_score(job_data)
                
                # Only create matches with meaningful scores (above 20%)
                if match_score >= 20:
                    # Create or update JobMatch record
                    with transaction.atomic():
                        job_match, created = JobMatch.objects.update_or_create(
                            job=job,
                            resume=resume,
                            user=resume.user,
                            defaults={
                                'match_score': match_score,
                                'matching_skills': match_details.get('matching_skills', []),
                                'missing_skills': match_details.get('missing_skills', []),
                                'match_details': match_details
                            }
                        )
                        
                        if created:
                            matches_created += 1
                            logger.debug(f"Created job match: {job.title} ({match_score:.1f}%)")
                        else:
                            logger.debug(f"Updated job match: {job.title} ({match_score:.1f}%)")
                            
            except Exception as e:
                logger.error(f"Error matching job {job.id} ({job.title}): {e}")
                continue
        
        logger.info(f"Job matching completed. Created {matches_created} new matches for resume {resume.id}")
        
    except Exception as e:
        logger.error(f"Error in find_matching_jobs for resume {resume.id}: {e}")
        raise
