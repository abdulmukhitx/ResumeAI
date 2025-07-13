from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.apps import apps
from django.db import IntegrityError
import os
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm
from .decorators import jwt_login_required

# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
JobApplication = apps.get_model('jobs', 'JobApplication')

def register_view(request):
    """
    Brand new simple register page - 100% working
    """
    return render(request, 'registration/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Authenticate using email as username
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                remember_me = request.POST.get('remember_me')
                if not remember_me:
                    request.session.set_expiry(0)
                
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def jwt_login_view(request):
    """
    Brand new simple login page - 100% working
    """
    return render(request, 'registration/login.html')

def logout_view(request):
    """
    Unified logout that handles both session and JWT authentication
    """
    # Clear session if exists
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    
    # The frontend JWT manager will handle JWT token cleanup
    return redirect('login')

@jwt_login_required
def profile_view(request):
    user = request.user
    
    # Fix profile picture issues
    try:
        if user.profile_picture and hasattr(user.profile_picture, 'name'):
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)):
                user.profile_picture = None
                user.save(update_fields=['profile_picture'])
    except ValueError:
        user.profile_picture = None
        user.save(update_fields=['profile_picture'])
    
    # Get resumes with analysis data
    resumes = Resume.objects.filter(user=user).order_by('-created_at')
    user_resume = resumes.first()
    
    # Get job applications
    job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
    
    # Get user profile data
    profile_data = None
    if hasattr(user, 'profile'):
        profile_data = user.profile
    
    # Calculate statistics
    total_resumes = resumes.count()
    completed_resumes = resumes.filter(status='completed').count()
    pending_resumes = resumes.filter(status='pending').count()
    failed_resumes = resumes.filter(status='failed').count()
    
    # Get skills from latest resume
    latest_skills = []
    if user_resume and user_resume.extracted_skills:
        latest_skills = user_resume.extracted_skills[:10]  # Top 10 skills
    
    # Get experience level from latest resume
    experience_level = None
    if user_resume and user_resume.experience_level:
        experience_level = user_resume.experience_level
    
    # Get job titles from latest resume
    job_titles = []
    if user_resume and user_resume.job_titles:
        job_titles = user_resume.job_titles[:5]  # Top 5 job titles
    elif user_resume and user_resume.work_experience:
        # Extract job titles from work experience if not directly available
        job_titles = []
        for exp in user_resume.work_experience[:5]:
            if isinstance(exp, dict) and exp.get('position'):
                job_titles.append(exp['position'])
            elif isinstance(exp, str):
                job_titles.append(exp)
    
    # Get education from latest resume
    education = []
    if user_resume and user_resume.education:
        education = user_resume.education
    
    # Get work experience from latest resume
    work_experience = []
    if user_resume and user_resume.work_experience:
        work_experience = user_resume.work_experience
    
    # Create analysis summary
    analysis_summary = None
    if user_resume and user_resume.analysis_summary:
        analysis_summary = user_resume.analysis_summary
    
    # Calculate confidence score
    confidence_score = None
    if user_resume and user_resume.confidence_score:
        confidence_score = user_resume.confidence_score
    
    context = {
        'user_resume': user_resume,
        'resumes': resumes,
        'job_applications': job_applications,
        'profile_data': profile_data,
        'total_resumes': total_resumes,
        'completed_resumes': completed_resumes,
        'pending_resumes': pending_resumes,
        'failed_resumes': failed_resumes,
        'latest_skills': latest_skills,
        'experience_level': experience_level,
        'job_titles': job_titles,
        'education': education,
        'work_experience': work_experience,
        'analysis_summary': analysis_summary,
        'confidence_score': confidence_score,
        'applications': job_applications,
    }
    return render(request, 'accounts/profile_enhanced.html', context)

@jwt_login_required
def edit_profile_view(request):
    # Check and fix profile picture issues before displaying the form
    user = request.user
    try:
        if user.profile_picture and hasattr(user.profile_picture, 'name'):
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)):
                user.profile_picture = None
                user.save(update_fields=['profile_picture'])
    except ValueError:
        user.profile_picture = None
        user.save(update_fields=['profile_picture'])
    
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileEditForm(instance=user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def jwt_demo_view(request):
    """
    JWT authentication demo page
    """
    return render(request, 'jwt_demo.html')

def simple_login_view(request):
    """Simple login view that renders the working template with proper context"""
    if request.user.is_authenticated:
        return redirect('home')
    
    # Provide context for the template
    context = {
        'next': request.GET.get('next', '/'),
    }
    
    return render(request, 'registration/login.html', context)
