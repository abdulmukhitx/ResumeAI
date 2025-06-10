from celery import shared_task
from django.utils import timezone
from django.apps import apps
from .utils import PDFProcessor, AIAnalyzer
import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def analyze_resume_task(self, resume_id):
    """Analyze uploaded resume using AI"""
    try:
        Resume = apps.get_model('resumes', 'Resume')  # Dynamically load the Resume model
        resume = Resume.objects.get(id=resume_id)

        # Update status to processing
        resume.status = 'processing'
        resume.analysis_started_at = timezone.now()
        resume.save()

        # Extract text from PDF
        pdf_processor = PDFProcessor()
        resume_text = pdf_processor.extract_text_from_pdf(resume.file.path)
        resume.raw_text = resume_text
        resume.save()

        # Analyze with AI
        ai_analyzer = AIAnalyzer()
        analysis_result = ai_analyzer.analyze_resume(resume_text)

        # Update resume with analysis results
        resume.extracted_skills = analysis_result.get('skills', [])
        resume.experience_level = analysis_result.get('experience_level', '')
        resume.job_titles = analysis_result.get('job_titles', [])
        resume.education = analysis_result.get('education', [])
        resume.work_experience = analysis_result.get('work_experience', [])
        resume.analysis_summary = analysis_result.get('summary', '')
        resume.confidence_score = analysis_result.get('confidence_score', 0.0)

        resume.status = 'completed'
        resume.analysis_completed_at = timezone.now()
        resume.save()

        # Update user profile with extracted skills
        user_profile = resume.user.profile
        user_profile.skills = resume.extracted_skills
        user_profile.save()

        logger.info("Resume analysis completed for user %s", resume.user.email)

        return {
            'status': 'success',
            'resume_id': resume_id,
            'skills_count': len(resume.extracted_skills),
            'confidence_score': resume.confidence_score
        }

    except ObjectDoesNotExist:
        logger.error("Resume with ID %s not found", resume_id)
        return {'status': 'error', 'message': 'Resume not found'}

    except (IOError, ValueError, KeyError) as exc:
        logger.error("Resume analysis failed for ID %s: %s", resume_id, str(exc))

        # Update resume status to failed
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.status = 'failed'
            resume.save()
        except ObjectDoesNotExist:
            pass

        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)

        return {'status': 'error', 'message': str(exc)}
