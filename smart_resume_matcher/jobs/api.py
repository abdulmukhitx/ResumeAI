from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.apps import apps
from accounts.decorators import jwt_login_required
import html
import re

# Get the model dynamically to avoid circular imports
Job = apps.get_model('jobs', 'Job')

@jwt_login_required
@require_GET
def get_formatted_job_description(request, job_id):
    """
    Returns a formatted job description suitable for display.
    This endpoint can be used by JavaScript to fetch and display
    properly formatted job descriptions.
    """
    try:
        job = Job.objects.get(id=job_id)
        description = format_description_text(job.description)
        requirements = format_description_text(job.requirements)
        
        return JsonResponse({
            'success': True,
            'job_id': job_id,
            'formatted_description': description,
            'formatted_requirements': requirements
        })
    except Job.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while formatting the job description'
        }, status=500)

def format_description_text(text):
    """
    Format job description text to be more user-friendly
    """
    if not text:
        return ""
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Process specific formatting patterns
    # Handle paragraphs and sections
    text = re.sub(r'<p>\s*<strong>(.*?)</strong>\s*</p>', r'\n\n## \1\n', text, flags=re.DOTALL)
    
    # Process lists
    text = re.sub(r'<ul>(.*?)</ul>', process_list, text, flags=re.DOTALL)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]*>', ' ', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # Trim whitespace
    return text.strip()

def process_list(match):
    """Process <ul> list into formatted bullet points"""
    list_content = match.group(1)
    items = re.findall(r'<li>(.*?)</li>', list_content, re.DOTALL)
    
    formatted_list = '\n'
    for item in items:
        formatted_list += f"• {item.strip()}\n"
    
    return formatted_list
