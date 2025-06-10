from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.apps import apps
import os
from .forms import UserRegistrationForm, UserLoginForm, UserProfileEditForm

# Dynamically load models to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
JobApplication = apps.get_model('jobs', 'JobApplication')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Smart Resume Matcher.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # The username could be either an email or a username
            user = authenticate(request, username=username, password=password)
            
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
        form = UserLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    # Use a safer approach to check profile picture
    try:
        if user.profile_picture and hasattr(user.profile_picture, 'name'):
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, user.profile_picture.name)):
                user.profile_picture = None
                user.save(update_fields=['profile_picture'])
    except ValueError:
        # If there's any issue with the profile picture, reset it
        user.profile_picture = None
        user.save(update_fields=['profile_picture'])
    
    user_resume = Resume.objects.filter(user=user).order_by('-created_at').first()
    job_applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
    
    context = {
        'user_resume': user_resume,
        'job_applications': job_applications,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
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
