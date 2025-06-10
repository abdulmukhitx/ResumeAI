from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, JobMatch, JobApplication, JobSearch
from .services import HHApiClient
from resumes.models import Resume
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator

@login_required
def job_list_view(request):
    """View to display all jobs"""
    # Get latest user resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    if not user_resume:
        messages.warning(request, "Please upload your resume to see job matches.")
        return redirect('resume_upload')
    
    # Get all jobs with their match scores
    job_matches = JobMatch.objects.filter(resume=user_resume).select_related('job')
    
    # Filter options
    match_filter = request.GET.get('match', None)
    if match_filter == 'high':
        job_matches = job_matches.filter(match_score__gte=75)
    elif match_filter == 'medium':
        job_matches = job_matches.filter(match_score__gte=50, match_score__lt=75)
    elif match_filter == 'low':
        job_matches = job_matches.filter(match_score__lt=50)
    
    # Get unique skills from user's resume
    user_skills = set(user_resume.extracted_skills)
    
    # Order by match score
    job_matches = job_matches.order_by('-match_score')
    
    # Pagination
    paginator = Paginator(job_matches, 10)
    page_number = request.GET.get('page', 1)
    job_matches_page = paginator.get_page(page_number)
    
    context = {
        'job_matches': job_matches_page,
        'user_skills': user_skills,
        'match_filter': match_filter
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def job_search_view(request):
    """View to search for jobs"""
    # Get user's resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    if not user_resume:
        messages.warning(request, "Please upload your resume to search for jobs.")
        return redirect('resume_upload')
    
    # Initialize search results
    jobs = []
    search_performed = False
    
    if request.method == 'POST':
        search_performed = True
        query = request.POST.get('query', '')
        location = request.POST.get('location', '')
        
        # Create JobSearch record
        job_search = JobSearch.objects.create(
            user=request.user,
            resume=user_resume,
            search_query=query,
            location=location,
            status='processing',
            started_at=timezone.now()
        )
        
        try:
            # Search for jobs using HH.ru API
            client = HHApiClient()
            search_params = {
                'text': query,
                'page': 0,
                'per_page': 20
            }
            
            # Only add area parameter if location is provided - empty string causes API error
            if location and location.strip():
                search_params['area'] = location
            
            search_results = client.search_vacancies(search_params)
            
            # Update JobSearch record
            job_search.total_found = search_results.get('found', 0)
            job_search.status = 'completed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Process job results
            for item in search_results.get('items', []):
                # Check if job already exists in DB
                job, created = Job.objects.get_or_create(
                    hh_id=item['id'],
                    defaults={
                        'title': item['name'],
                        'company_name': item['employer']['name'],
                        'company_url': item['employer'].get('alternate_url', ''),
                        'description': item.get('snippet', {}).get('responsibility', ''),
                        'requirements': item.get('snippet', {}).get('requirement', ''),
                        'salary_from': item.get('salary', {}).get('from'),
                        'salary_to': item.get('salary', {}).get('to'),
                        'salary_currency': item.get('salary', {}).get('currency'),
                        'location': item.get('area', {}).get('name', ''),
                        'employment_type': item.get('employment', {}).get('name', ''),  # Fixed field name
                        'hh_url': item.get('alternate_url', ''),  # Fixed field name
                        'published_at': item.get('published_at') or timezone.now(),
                        'is_active': True
                    }
                )
                
                # If needed, fetch more details using vacancy_id
                if created and item.get('id'):
                    try:
                        details = client.get_vacancy_details(item['id'])
                        # Update with more details if needed
                        job.description = details.get('description', job.description)
                        # Add other fields as needed
                        job.save()
                    except Exception:
                        # Handle error, continue with basic job info
                        pass
                
                jobs.append(job)
            
            # Success message
            messages.success(request, f"Found {len(jobs)} jobs matching your search.")
            
        except Exception as e:
            # Update JobSearch record with error
            job_search.status = 'failed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Error message
            messages.error(request, f"Error searching for jobs: {str(e)}")
    
    context = {
        'jobs': jobs,
        'search_performed': search_performed,
        'user_resume': user_resume
    }
    return render(request, 'jobs/job_search.html', context)

@login_required
def job_detail_view(request, job_id):
    """View job details"""
    job = get_object_or_404(Job, id=job_id)
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    # Get job match score if available
    job_match = None
    if user_resume:
        job_match = JobMatch.objects.filter(job=job, resume=user_resume).first()
    
    # Check if user already applied
    application = JobApplication.objects.filter(job=job, user=request.user).first()
    
    context = {
        'job': job,
        'job_match': job_match,
        'application': application,
        'user_resume': user_resume
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def job_application_view(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user already applied
    existing_application = JobApplication.objects.filter(job=job, user=request.user).exists()
    if existing_application:
        messages.info(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job_id)
    
    # Get user resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    if not user_resume:
        messages.error(request, "You need to upload a resume before applying for jobs.")
        return redirect('resume_upload')
    
    # Get match score if available
    try:
        job_match = JobMatch.objects.get(job=job, resume=user_resume)
        match_score = job_match.match_score
    except JobMatch.DoesNotExist:
        match_score = 0
    
    if request.method == 'POST':
        # Create application
        application = JobApplication.objects.create(
            user=request.user,
            job=job,
            resume=user_resume,
            match_score=match_score,
            cover_letter=request.POST.get('cover_letter', ''),
            status='applied',
            applied_date=timezone.now()
        )
        
        messages.success(request, f"Successfully applied for {job.title}!")
        return redirect('job_detail', job_id=job_id)
    
    context = {
        'job': job,
        'user_resume': user_resume,
        'match_score': match_score
    }
    return render(request, 'jobs/job_application.html', context)
