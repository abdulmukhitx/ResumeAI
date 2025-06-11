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

@login_required
def resume_upload_view(request):
    # Check if user already has a resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).order_by('-created_at').first()
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            from django.db import transaction
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                with transaction.atomic():
                    # Create new resume instance but don't save yet
                    resume = form.save(commit=False)
                    resume.user = request.user
                    resume.original_filename = request.FILES['file'].name
                    resume.file_size = request.FILES['file'].size
                    
                    # If user already has a resume, mark it as inactive
                    if user_resume:
                        user_resume.is_active = False
                        user_resume.save()
                    
                    # Save the new resume
                    resume.save()
                
                # Start the analysis process (in real app, this would be a Celery task)
                # This is done outside the transaction to avoid long-running transactions
                try:
                    analyze_resume(resume.id)
                    messages.success(request, 'Resume uploaded and analyzed successfully!')
                except Exception as e:
                    logger.error(f"Resume analysis error: {str(e)}")
                    # Update resume status in a separate transaction
                    try:
                        with transaction.atomic():
                            resume.refresh_from_db()
                            resume.status = 'failed'
                            resume.save()
                    except Exception:
                        pass  # If we can't update status, that's okay
                    messages.error(request, 'We encountered an issue while analyzing your resume. Please try again later.')
                
                return redirect('profile')
                
            except Exception as e:
                logger.error(f"Resume upload error: {str(e)}")
                messages.error(request, 'There was an error uploading your resume. Please try again.')
                
    else:
        form = ResumeUploadForm()
    
    context = {
        'form': form,
        'user_resume': user_resume
    }
    return render(request, 'resumes/upload.html', context)

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
