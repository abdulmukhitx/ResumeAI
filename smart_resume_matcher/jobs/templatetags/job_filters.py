from django import template
import html
import re

register = template.Library()

@register.filter(name='filter_by_resume')
def filter_by_resume(matches, resume):
    """
    Filter job matches by a specific resume
    Usage: {{ job.matches.all|filter_by_resume:user_resume }}
    """
    if not resume or not matches:
        return None
    
    try:
        for match in matches:
            if match and hasattr(match, 'resume_id') and match.resume_id == resume.id:
                return match
    except Exception:
        # Handle any unexpected errors gracefully
        return None
    
    return None

@register.filter(name='clean_html_description')
def clean_html_description(value):
    """
    Filter to properly format and clean HTML job descriptions.
    Removes HTML tags and formats line breaks for better readability.
    """
    if not value:
        return ""
    
    # Special handling for the job description format seen in the screenshot
    # First check for common patterns in the data
    if '<p>' in value and '<strong>' in value and '</strong>' in value:
        # Unescape HTML entities first
        value = html.unescape(value)
        
        # Process headings and important text
        value = re.sub(r'<p><strong>(.*?)</strong></p>', r'\n\n\1:\n', value, flags=re.DOTALL)
        
        # Convert <p> tags to paragraphs with line breaks
        value = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', value, flags=re.DOTALL)
        
        # Convert <ul> and <li> to bullet points
        value = re.sub(r'<ul[^>]*>(.*?)</ul>', r'\n\1', value, flags=re.DOTALL)
        value = re.sub(r'<li[^>]*>(.*?)</li>', r'• \1\n', value, flags=re.DOTALL)
        
        # Convert <strong> and <b> to make text stand out
        value = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'\2', value, flags=re.DOTALL)
        
        # Remove all other HTML tags
        value = re.sub(r'<[^>]*>', ' ', value)
        
        # Fix multiple spaces and line breaks
        value = re.sub(r' +', ' ', value)
        value = re.sub(r'\n{3,}', '\n\n', value)
        
        # Handle specific content formatting
        value = value.replace('Кто мы и чем занимаемся:', '\nAbout Us:')
        value = value.replace('Наши проекты:', '\nOur Projects:')
        value = value.replace('Тогда мы ищем именно ВАС!', '\nWe are looking for YOU!')
        value = value.replace('Здесь вы научитесь:', '\nWhat You Will Learn:')
        value = value.replace('Вы должны знать:', '\nRequired Skills:')
        
        # Trim leading/trailing whitespace
        value = value.strip()
    else:
        # Default handling for other formats
        # Unescape HTML entities first
        value = html.unescape(value)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', ' ', value)
        
        # Fix spaces
        value = re.sub(r' +', ' ', value)
        value = value.strip()
    
    return value

@register.filter(name='match_score_class')
def match_score_class(score):
    """
    Return appropriate CSS class based on match score
    Usage: {{ job_match.match_score|match_score_class }}
    """
    try:
        score_val = float(score)
        if score_val >= 75:
            return 'bg-success'
        elif score_val >= 50:
            return 'bg-info'
        elif score_val >= 30:
            return 'bg-warning'
        else:
            return 'bg-danger'
    except (ValueError, TypeError):
        return 'bg-secondary'
