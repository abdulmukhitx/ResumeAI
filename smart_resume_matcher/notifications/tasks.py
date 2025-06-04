from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import EmailNotification
from jobs.models import JobSearch, JobMatch
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, notification_id):
    """Send email notification"""
    try:
        notification = EmailNotification.objects.get(id=notification_id)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=notification.subject,
            body=notification.text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notification.user.email]
        )
        
        if notification.html_content:
            email.attach_alternative(notification.html_content, "text/html")
        
        # Send email
        email.send()
        
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.save()
        
        logger.info(f"Email sent successfully to {notification.user.email}")
        return {'status': 'success', 'notification_id': notification_id}
        
    except EmailNotification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'status': 'error', 'message': 'Notification not found'}
    
    except Exception as exc:
        logger.error(f"Failed to send email notification {notification_id}: {str(exc)}")
        
        # Update notification with error
        try:
            notification = EmailNotification.objects.get(id=notification_id)
            notification.status = 'failed'
            notification.error_message = str(exc)
            notification.save()
        except:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
        
        return {'status': 'error', 'message': str(exc)}

@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Render email content
        html_content = render_to_string('emails/welcome.html', {
            'user': user,
            'site_name': 'Smart Resume Matcher'
        })
        
        text_content = render_to_string('emails/welcome.txt', {
            'user': user,
            'site_name': 'Smart Resume Matcher'
        })
        
        # Create notification record
        notification = EmailNotification.objects.create(
            user=user,
            email_type='welcome',
            subject='Welcome to Smart Resume Matcher!',
            html_content=html_content,
            text_content=text_content
        )
        
        # Send email
        send_email_notification.delay(notification.id)
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for welcome email")

@shared_task
def send_resume_analyzed_email(user_id, resume_id):
    """Send email when resume analysis is complete"""
    try:
        user = User.objects.get(id=user_id)
        resume = user.resumes.get(id=resume_id)
        
        # Render email content
        html_content = render_to_string('emails/resume_analyzed.html', {
            'user': user,
            'resume': resume,
            'skills_count': len(resume.extracted_skills),
            'confidence_score': resume.confidence_score
        })
        
        text_content = render_to_string('emails/resume_analyzed.txt', {
            'user': user,
            'resume': resume,
            'skills_count': len(resume.extracted_skills)
        })
        
        # Create notification record
        notification = EmailNotification.objects.create(
            user=user,
            email_type='resume_analyzed',
            subject='Your Resume Analysis is Complete!',
            html_content=html_content,
            text_content=text_content,
            resume_id=resume_id
        )
        
        # Send email
        send_email_notification.delay(notification.id)
        
    except (User.DoesNotExist, User.resumes.model.DoesNotExist):
        logger.error(f"User {user_id} or resume {resume_id} not found")

@shared_task
def send_job_matches_email(user_id, job_search_id):
    """Send email with new job matches"""
    try:
        user = User.objects.get(id=user_id)
        job_search = JobSearch.objects.get(id=job_search_id)
        
        # Get top matches
        top_matches = JobMatch.objects.filter(
            user=user,
            job_search=job_search
        ).order_by('-overall_score')[:5]
        
        if not top_matches:
            return
        
        # Render email content
        html_content = render_to_string('emails/job_matches.html', {
            'user': user,
            'job_search': job_search,
            'matches': top_matches,
            'total_matches': job_search.matches_found
        })
        
        text_content = render_to_string('emails/job_matches.txt', {
            'user': user,
            'job_search': job_search,
            'matches': top_matches,
            'total_matches': job_search.matches_found
        })
        
        # Create notification record
        notification = EmailNotification.objects.create(
            user=user,
            email_type='job_matches',
            subject=f'Found {job_search.matches_found} Job Matches for You!',
            html_content=html_content,
            text_content=text_content,
            job_search_id=job_search_id
        )
        
        # Send email
        send_email_notification.delay(notification.id)
        
    except (User.DoesNotExist, JobSearch.DoesNotExist):
        logger.error(f"User {user_id} or job search {job_search_id} not found")
