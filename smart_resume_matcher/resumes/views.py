from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.apps import apps
from .forms import ResumeUploadForm
from .utils import AIAnalyzer
from jobs.services import JobMatcher

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
        # Initialize AI analyzer
        analyzer = AIAnalyzer()
        
        # Extract text from PDF
        try:
            resume.raw_text = analyzer.extract_text_from_pdf(resume.file.path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # If PDF extraction fails, set a placeholder and continue
            resume.raw_text = "Error extracting text from resume."
        
        # Save the raw text first
        resume.save(update_fields=['raw_text'])
            
        # Analyze the resume - this will use fallback if AI isn't available
        analysis_results = analyzer.analyze_resume(resume.raw_text)
        
        # Update resume with analysis results in a single transaction
        with transaction.atomic():
            resume.refresh_from_db()
            resume.extracted_skills = analysis_results.get('skills', [])
            resume.experience_level = analysis_results.get('experience_level', '')
            resume.job_titles = analysis_results.get('job_titles', [])
            resume.education = analysis_results.get('education', [])
            resume.work_experience = analysis_results.get('work_experience', [])
            resume.analysis_summary = analysis_results.get('summary', '')
            resume.confidence_score = analysis_results.get('confidence_score', 0.0)
            
            # Update status
            resume.status = 'completed'
            resume.analysis_completed_at = timezone.now()
            resume.save()
        
        # Find matching jobs - wrap in try/except to ensure process completes
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
    # Get active jobs
    active_jobs = Job.objects.filter(is_active=True)
    
    # Prepare resume data
    resume_data = {
        'extracted_skills': resume.extracted_skills,
        'experience_level': resume.experience_level,
        'job_titles': resume.job_titles
    }
    
    # Initialize job matcher
    matcher = JobMatcher()
    
    # Dynamically import JobMatch model to avoid circular imports
    JobMatch = apps.get_model('jobs', 'JobMatch')
    
    # Match jobs
    for job in active_jobs:
        job_data = {
            'title': job.title,
            'required_skills': job.required_skills,
            'experience_required': job.experience_required
        }
        
        # Calculate match score
        match_result = matcher.calculate_match_score(resume_data, job_data)
        
        # Create or update JobMatch record
        job_match, created = JobMatch.objects.update_or_create(
            job=job,
            resume=resume,
            user=resume.user,
            defaults={
                'match_score': match_result['overall_score'] * 100,  # Convert to percentage
                'matching_skills': match_result['matched_skills'],
                'missing_skills': match_result['missing_skills'],
                'match_details': match_result
            }
        )
        
        # Create or update JobMatch record (implementation depends on your model structure)
