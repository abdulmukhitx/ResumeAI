from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume
from .forms import ResumeUploadForm
from .utils import AIAnalyzer
from django.utils import timezone
from jobs.services import JobMatcher
from jobs.models import Job

@login_required
def resume_upload_view(request):
    # Check if user already has a resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).order_by('-created_at').first()
    
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
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
            try:
                analyze_resume(resume.id)
                messages.success(request, 'Resume uploaded and analyzed successfully!')
            except Exception as e:
                resume.status = 'failed'
                resume.save()
                messages.error(request, f'Error analyzing resume: {str(e)}')
            
            return redirect('profile')
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
    resume = Resume.objects.get(id=resume_id)
    resume.status = 'processing'
    resume.analysis_started_at = timezone.now()
    resume.save()
    
    try:
        # Initialize AI analyzer
        analyzer = AIAnalyzer()
        
        # Extract text from PDF
        resume.raw_text = analyzer.extract_text_from_pdf(resume.file.path)
        
        # Analyze the resume
        analysis_results = analyzer.analyze_resume(resume.raw_text)
        
        # Update resume with analysis results
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
        
        # Find matching jobs
        find_matching_jobs(resume)
        
        return True
    except Exception as e:
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
    
    # Match jobs
    for job in active_jobs:
        job_data = {
            'title': job.title,
            'required_skills': job.required_skills,
            'experience_required': job.experience_required
        }
        
        # Calculate match score
        match_result = matcher.calculate_match_score(resume_data, job_data)
        
        # Create or update JobMatch record (implementation depends on your model structure)
