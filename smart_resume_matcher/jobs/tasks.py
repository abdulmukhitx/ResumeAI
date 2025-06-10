from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.apps import apps
from datetime import timedelta
from .services import HHApiClient, JobMatcher
from notifications.tasks import send_job_matches_email
import logging

User = get_user_model()
# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
JobSearch = apps.get_model('jobs', 'JobSearch')
Job = apps.get_model('jobs', 'Job')
JobMatch = apps.get_model('jobs', 'JobMatch')
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def search_and_match_jobs_task(self, user_id, resume_id):
    """Search for jobs and create matches for a specific user"""
    try:
        user = User.objects.get(id=user_id)
        resume = Resume.objects.get(id=resume_id, user=user, status='completed')
        
        # Create job search record
        job_search = JobSearch.objects.create(
            user=user,
            resume=resume,
            search_query=user.profile.desired_position or 'Software Developer',
            location=user.profile.preferred_locations[0] if user.profile.preferred_locations else '',
            salary_from=user.profile.min_salary,
            salary_to=user.profile.max_salary,
            experience_level=user.profile.experience_level,
            status='processing',
            started_at=timezone.now()
        )
        
        # Initialize services
        hh_client = HHApiClient()
        job_matcher = JobMatcher()
        
        # Prepare search parameters
        search_params = {
            'text': job_search.search_query,
            'per_page': 50,  # Max results per page
            'page': 0,
        }
        
        # Only set area if you have a valid location code (default to Moscow if needed)
        if job_search.location and job_search.location.strip():
            # Try to use the provided location
            search_params['area'] = job_search.location
        else:
            # Default to Moscow (area code 1) as fallback
            search_params['area'] = 1
        
        if job_search.salary_from:
            search_params['salary'] = job_search.salary_from
        
        # Search for jobs
        search_result = hh_client.search_vacancies(search_params)
        job_search.total_found = search_result.get('found', 0)
        job_search.save()
        
        matches_created = 0
        jobs_processed = 0
        
        # Process each job
        for vacancy in search_result.get('items', [])[:20]:  # Limit to 20 jobs to avoid rate limits
            try:
                # Get detailed job information
                job_details = hh_client.get_vacancy_details(vacancy['id'])
                
                # Create or update job record
                job, created = Job.objects.update_or_create(
                    hh_id=vacancy['id'],
                    defaults={
                        'title': job_details.get('name', ''),
                        'company_name': job_details.get('employer', {}).get('name', ''),
                        'company_url': job_details.get('employer', {}).get('alternate_url', ''),
                        'description': job_details.get('description', ''),
                        'requirements': job_details.get('key_skills', []),
                        'location': job_details.get('area', {}).get('name', ''),
                        'salary_from': job_details.get('salary', {}).get('from') if job_details.get('salary') else None,
                        'salary_to': job_details.get('salary', {}).get('to') if job_details.get('salary') else None,
                        'salary_currency': job_details.get('salary', {}).get('currency', 'RUB') if job_details.get('salary') else 'RUB',
                        'employment_type': job_details.get('employment', {}).get('name', ''),
                        'experience_required': job_details.get('experience', {}).get('name', ''),
                        'required_skills': [skill['name'] for skill in job_details.get('key_skills', [])],
                        'hh_url': job_details.get('alternate_url', ''),
                        'published_at': timezone.now(),  # You can parse the actual date from HH
                    }
                )
                
                jobs_processed += 1
                
                # Calculate match score
                resume_data = {
                    'extracted_skills': resume.extracted_skills,
                    'experience_level': resume.experience_level,
                    'job_titles': resume.job_titles,
                }
                
                job_data = {
                    'title': job.title,
                    'required_skills': job.required_skills,
                    'experience_required': job.experience_required,
                }
                
                match_result = job_matcher.calculate_match_score(resume_data, job_data)
                
                # Only create matches above threshold
                if match_result['overall_score'] >= 0.3:  # 30% threshold
                    JobMatch.objects.create(
                        user=user,
                        job=job,
                        resume=resume,
                        job_search=job_search,
                        overall_score=match_result['overall_score'],
                        skills_score=match_result['skills_score'],
                        experience_score=match_result['experience_score'],
                        title_score=match_result['title_score'],
                        matched_skills=match_result['matched_skills'],
                        missing_skills=match_result['missing_skills'],
                        match_explanation=match_result['match_explanation'],
                    )
                    matches_created += 1
                
            except Exception as e:
                logger.error(f"Error processing job {vacancy['id']}: {str(e)}")
                continue
        
        # Update job search results
        job_search.jobs_analyzed = jobs_processed
        job_search.matches_found = matches_created
        job_search.status = 'completed'
        job_search.completed_at = timezone.now()
        job_search.save()
        
        # Update user's last job search
        user.profile.last_job_search = timezone.now()
        user.profile.save()
        
        # Send email notification if matches found
        if matches_created > 0:
            send_job_matches_email.delay(user_id, job_search.id)
        
        logger.info(f"Job search completed for user {user.email}: {matches_created} matches found")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'jobs_processed': jobs_processed,
            'matches_created': matches_created
        }
        
    except Exception as exc:
        logger.error(f"Job search failed for user {user_id}: {str(exc)}")
        
        # Update job search status to failed
        try:
            job_search.status = 'failed'
            job_search.save()
        except:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
        
        return {'status': 'error', 'message': str(exc)}

@shared_task
def weekly_job_search_for_all_users():
    """Run weekly job search for all active users"""
    active_users = User.objects.filter(
        profile__is_job_search_active=True,
        profile__weekly_job_emails=True,
        resumes__status='completed'
    ).distinct()
    
    count = 0
    for user in active_users:
        # Check if user hasn't had a job search in the last week
        if (not user.profile.last_job_search or 
            user.profile.last_job_search < timezone.now() - timedelta(days=7)):
            
            # Get user's latest completed resume
            latest_resume = user.resumes.filter(status='completed').first()
            if latest_resume:
                search_and_match_jobs_task.delay(user.id, latest_resume.id)
                count += 1
    
    logger.info(f"Scheduled weekly job search for {count} users")
    return {'scheduled_searches': count}