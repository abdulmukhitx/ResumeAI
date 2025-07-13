from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.apps import apps
from .services import HHApiClient
from .job_matcher import JobMatcher
from .enhanced_hh_client import EnhancedHHApiClient
from .realtime_matcher import RealTimeJobMatcher
from resumes.enhanced_job_matcher import AdvancedJobMatcher
from accounts.decorators import jwt_login_required

# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
JobMatch = apps.get_model('jobs', 'JobMatch')
Job = apps.get_model('jobs', 'Job')
JobApplication = apps.get_model('jobs', 'JobApplication')
JobSearch = apps.get_model('jobs', 'JobSearch')

@jwt_login_required
def job_list_view(request):
    """View to display all jobs with enhanced matching"""
    # Get latest user resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    if not user_resume:
        messages.warning(request, "Please upload your resume to see job matches.")
        return redirect('jwt_resume_upload')
    
    # Create enhanced job matcher
    enhanced_matcher = AdvancedJobMatcher(user=request.user, resume=user_resume)
    
    # Try to get existing job matches, if none exist, generate them
    job_matches = JobMatch.objects.filter(resume=user_resume).select_related('job')
    
    if not job_matches.exists():
        # Generate enhanced job matches
        try:
            import asyncio
            enhanced_matches = asyncio.run(enhanced_matcher.generate_advanced_job_matches(limit=20))
            
            # Create JobMatch objects from enhanced matches
            for match_data in enhanced_matches:
                if match_data.get('job'):
                    job = match_data['job']
                    JobMatch.objects.get_or_create(
                        job=job,
                        resume=user_resume,
                        defaults={
                            'user': request.user,
                            'match_score': match_data.get('match_score', 0),
                            'match_details': match_data.get('match_details', {}),
                            'matching_skills': match_data.get('matching_skills', []),
                            'missing_skills': match_data.get('missing_skills', [])
                        }
                    )
            
            job_matches = JobMatch.objects.filter(resume=user_resume).select_related('job')
            if job_matches.exists():
                messages.success(request, f"Generated {job_matches.count()} enhanced job matches based on your skills!")
        except Exception as e:
            messages.warning(request, f"Could not generate enhanced matches: {e}")
    
    # Filter options
    match_filter = request.GET.get('match', None)
    if match_filter == 'high':
        job_matches = job_matches.filter(match_score__gte=75)
    elif match_filter == 'medium':
        job_matches = job_matches.filter(match_score__gte=50, match_score__lt=75)
    elif match_filter == 'low':
        job_matches = job_matches.filter(match_score__lt=50)
    
    # Get unique skills from user's resume
    user_skills = set(user_resume.extracted_skills) if user_resume.extracted_skills else set()
    
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

@jwt_login_required
def ai_job_matches_view(request):
    """View to display AI-powered job matches fetched from HH.ru and HH.kz APIs"""
    # Get latest user resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    if not user_resume:
        messages.warning(request, "Please upload your resume to see AI job matches.")
        return redirect('jwt_resume_upload')
    
    # Import real-time matcher
    from .realtime_hh_client import RealTimeJobMatcher
    
    # Initialize variables
    jobs = []
    search_performed = False
    search_query = request.GET.get('search', '') or request.GET.get('query', '')
    location = request.GET.get('location', '')
    auto_match = request.GET.get('auto_match', False) == 'true'
    
    # Create real-time job matcher
    realtime_matcher = RealTimeJobMatcher(user=request.user, resume=user_resume)
    
    # Perform search if requested
    if auto_match or search_query or location:
        search_performed = True
        
        # For auto-match, use skills from resume
        if auto_match and not search_query:
            if user_resume.extracted_skills:
                # Use first few skills as search query
                search_query = ', '.join(user_resume.extracted_skills[:3])
        
        # Create JobSearch record
        job_search = JobSearch.objects.create(
            user=request.user,
            resume=user_resume,
            search_query=search_query,
            location=location,
            status='processing',
            started_at=timezone.now()
        )
        
        try:
            # Fetch jobs from HH.ru and HH.kz APIs in real-time
            matched_jobs = realtime_matcher.find_matching_jobs(
                search_query=search_query,
                location=location,
                limit=50
            )
            
            # Convert job dictionaries to job-like objects for template compatibility
            jobs = []
            for job_data in matched_jobs:
                # Handle date formatting for template compatibility
                published_at = job_data.get('published_at')
                if published_at:
                    try:
                        from datetime import datetime
                        if isinstance(published_at, str):
                            # Parse ISO format datetime string
                            published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        job_data['published_at'] = published_at
                    except (ValueError, TypeError):
                        # If parsing fails, set to current time
                        job_data['published_at'] = timezone.now()
                
                # Create a simple object that behaves like a Django model
                job_obj = type('Job', (), job_data)()
                jobs.append(job_obj)
            
            job_search.total_found = len(jobs)
            job_search.jobs_analyzed = len(jobs)
            job_search.matches_found = len(jobs)
            job_search.status = 'completed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Success message
            if jobs:
                messages.success(request, f"Found {len(jobs)} fresh job matches from HH.ru and HH.kz!")
            else:
                messages.info(request, "No matching jobs found. Try different search terms or location.")
        
        except Exception as e:
            # Update JobSearch record with error
            job_search.status = 'failed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Log the detailed error for admins
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Real-time job matching error: {str(e)}", exc_info=True)
            
            # User-friendly error message
            messages.error(request, f"Error fetching jobs from HH APIs: {str(e)}")
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page_number)
    
    # Create job matches for template compatibility
    job_matches = []
    if jobs_page:
        for job in jobs_page:
            # Create a match object from the job data
            match_obj = type('JobMatch', (), {
                'job': job,
                'match_score': getattr(job, 'match_score', 0),
                'matching_skills': getattr(job, 'matching_skills', []),
                'missing_skills': getattr(job, 'missing_skills', [])
            })()
            
            job_matches.append(match_obj)
    
    # Calculate statistics
    total_jobs = len(jobs)
    avg_match_score = 0
    top_skills_count = 0
    new_jobs_count = 0
    
    if job_matches:
        # Calculate average match score
        match_scores = [getattr(match, 'match_score', 0) for match in job_matches]
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0
        
        # Count unique skills
        all_skills = set()
        for match in job_matches:
            matching_skills = getattr(match, 'matching_skills', [])
            if isinstance(matching_skills, list):
                all_skills.update(matching_skills)
        top_skills_count = len(all_skills)
        
        # Count new jobs (assume all real-time jobs are new)
        new_jobs_count = len(job_matches)
    
    # Get user skills for template
    user_skills = []
    if user_resume and user_resume.extracted_skills:
        user_skills = user_resume.extracted_skills
    
    # Handle AJAX request for auto-match
    if auto_match and request.headers.get('Accept') == 'application/json':
        from django.http import JsonResponse
        
        matches_data = []
        for match in job_matches:
            job = match.job
            matches_data.append({
                'job': {
                    'id': getattr(job, 'id', 0),
                    'title': getattr(job, 'title', ''),
                    'company': getattr(job, 'company', ''),
                    'location': getattr(job, 'location', ''),
                    'description': getattr(job, 'description', ''),
                    'skills': getattr(job, 'skills', []),
                    'salary': getattr(job, 'salary', ''),
                    'posted_date': getattr(job, 'posted_date', ''),
                },
                'match_score': match.match_score
            })
        
        return JsonResponse({
            'success': True,
            'matches': matches_data,
            'stats': {
                'total_jobs': total_jobs,
                'avg_match': avg_match_score,
                'top_skills': top_skills_count,
                'new_jobs': new_jobs_count
            }
        })
    
    context = {
        'user_resume': user_resume,
        'jobs': jobs_page,
        'job_matches': job_matches,
        'avg_match_score': avg_match_score,
        'top_skills_count': top_skills_count,
        'new_jobs_count': new_jobs_count,
        'user_skills': user_skills,
        'search_performed': search_performed,
        'search_query': search_query,
        'location': location
    }
    
    return render(request, 'jobs/ai_job_matches.html', context)

@jwt_login_required
def job_search_view(request):
    """View to search for jobs"""
    # Get user's resume
    user_resume = Resume.objects.filter(user=request.user, is_active=True).first()
    
    if not user_resume:
        messages.warning(request, "Please upload your resume to search for jobs.")
        return redirect('jwt_resume_upload')
    
    # Initialize search results
    jobs = []
    search_performed = False
    
    if request.method == 'POST':
        search_performed = True
        query = request.POST.get('query', '')
        location = request.POST.get('location', '')
        use_ai_matching = request.POST.get('use_ai_matching', False) == 'on'
        
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
            
            # Only add area parameter if location is provided
            # HH.ru API expects numeric area IDs, not text names
            if location and location.strip():
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Processing location: {location}")
                
                # Try to identify common cities and map them to HH.ru area IDs
                location_mapping = {
                    'almaty': '160',
                    'nur-sultan': '159',  # Now Astana
                    'astana': '159',
                    'shymkent': '202',
                    'kazakhstan': '40',  # Country code
                    'moscow': '1',
                    'saint petersburg': '2',
                    'russia': '113'  # Country code
                }
                
                # Clean up location - remove commas and extra spaces
                location_parts = [part.strip().lower() for part in location.split(',')]
                location_lower = ' '.join(location_parts)
                
                # Try to match the location to a known city
                area_id = None
                for city, city_id in location_mapping.items():
                    if city in location_lower:
                        area_id = city_id
                        logger.info(f"Matched location '{location}' to city '{city}' with ID {area_id}")
                        break
                
                # If no match found but we have multiple parts, try each part separately
                if area_id is None and len(location_parts) > 1:
                    for part in location_parts:
                        for city, city_id in location_mapping.items():
                            if city in part:
                                area_id = city_id
                                logger.info(f"Matched location part '{part}' to city '{city}' with ID {area_id}")
                                break
                        if area_id:
                            break
                
                # If still no match but it's a numeric value, use it directly
                if area_id is None and location.strip().isdigit():
                    area_id = location.strip()
                    logger.info(f"Using location as numeric ID: {area_id}")
                
                # If we found a valid area ID, add it to the parameters
                if area_id:
                    search_params['area'] = area_id
                else:
                    logger.warning(f"Could not map location '{location}' to a valid area ID. Using default.")
            
            search_results = client.search_vacancies(search_params)
            
            # Update JobSearch record
            job_search.total_found = search_results.get('found', 0)
            job_search.status = 'completed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Process job results
            for item in search_results.get('items', []):
                # Skip items with missing required fields
                if 'id' not in item or 'name' not in item or 'employer' not in item:
                    continue
                
                # Safely get nested values
                company_name = item.get('employer', {}).get('name', 'Unknown Company')
                company_url = item.get('employer', {}).get('alternate_url', '')
                description = item.get('snippet', {}).get('responsibility', '') if item.get('snippet') else ''
                requirements = item.get('snippet', {}).get('requirement', '') if item.get('snippet') else ''
                salary_from = item.get('salary', {}).get('from') if item.get('salary') else None
                salary_to = item.get('salary', {}).get('to') if item.get('salary') else None
                salary_currency = item.get('salary', {}).get('currency', 'RUB') if item.get('salary') else 'RUB'
                location = item.get('area', {}).get('name', '') if item.get('area') else ''
                employment_type = item.get('employment', {}).get('name', '') if item.get('employment') else ''
                
                # Check if job already exists in DB
                job, created = Job.objects.get_or_create(
                    hh_id=item['id'],
                    defaults={
                        'title': item['name'],
                        'company_name': company_name,
                        'company_url': company_url,
                        'description': description,
                        'requirements': requirements,
                        'salary_from': salary_from,
                        'salary_to': salary_to,
                        'salary_currency': salary_currency,
                        'location': location,
                        'employment_type': employment_type,
                        'hh_url': item.get('alternate_url', ''),
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
                
                # Calculate match score if AI matching is enabled
                if use_ai_matching and user_resume:
                    try:
                        job_matcher = JobMatcher(user=request.user, resume=user_resume)
                        match_score, match_details = job_matcher.calculate_match_score(item)
                        
                        # Save match details
                        JobMatch.objects.update_or_create(
                            job=job,
                            resume=user_resume,
                            defaults={
                                'user': request.user,
                                'match_score': match_score,
                                'match_details': match_details,
                                'matching_skills': match_details.get('matching_skills', []),
                                'missing_skills': match_details.get('missing_skills', [])
                            }
                        )
                    except Exception as match_error:
                        logger.warning(f"Error calculating match score for job {job.id}: {str(match_error)}")
                        # Continue processing other jobs even if one fails
                
                jobs.append(job)
            
            # Success message
            messages.success(request, f"Found {len(jobs)} jobs matching your search.")
            
        except Exception as e:
            # Log detailed error
            logger.error(f"Job search error: {str(e)}", exc_info=True)
            
            # Update JobSearch record with error
            job_search.status = 'failed'
            job_search.completed_at = timezone.now()
            job_search.save()
            
            # Show user-friendly error message
            error_msg = str(e)
            if "NoneType" in error_msg:
                messages.error(request, "Error processing job data. Please try again with different search terms.")
            else:
                messages.error(request, f"Error searching for jobs: {error_msg}")
    
    context = {
        'jobs': jobs,
        'search_performed': search_performed,
        'user_resume': user_resume
    }
    return render(request, 'jobs/job_search.html', context)

@jwt_login_required
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

@jwt_login_required
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
        return redirect('jwt_resume_upload')
    
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
