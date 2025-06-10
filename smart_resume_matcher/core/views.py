from django.shortcuts import render
from jobs.models import JobMatch
from resumes.models import Resume
from django.conf import settings
import random

# AI tips for career development
CAREER_TIPS = [
    "Keep your resume updated with specific metrics and achievements.",
    "Tailor your resume keywords to match the job description you're applying for.",
    "Follow up after job interviews with a thank-you note highlighting your strengths.",
    "Consider joining industry-specific online communities to expand your network.",
    "Regularly update your skills to stay competitive in the job market.",
    "Practice mock interviews to build confidence and improve your responses.",
    "Create a personal portfolio to showcase your projects and achievements.",
    "Schedule informational interviews to learn about potential career paths.",
    "Set up job alerts on multiple platforms to stay informed about opportunities.",
    "Develop your soft skills as they are increasingly valued by employers."
]

def home_view(request):
    context = {}
    
    if request.user.is_authenticated:
        # Check if user has resume
        has_resume = Resume.objects.filter(user=request.user, is_active=True).exists()
        context['has_resume'] = has_resume
        
        if has_resume:
            # Get user's latest resume
            resume = Resume.objects.filter(user=request.user, is_active=True).latest('created_at')
            
            # Get job matches for the user
            job_matches = JobMatch.objects.filter(
                resume=resume, 
                match_score__gte=50  # Show only relevant matches (score >= 50%)
            ).select_related('job').order_by('-match_score')[:6]  # Get top 6 matches
            
            context['job_matches'] = job_matches
            
            # Add AI career tip
            context['ai_tip'] = random.choice(CAREER_TIPS)
    
    return render(request, 'home.html', context)
