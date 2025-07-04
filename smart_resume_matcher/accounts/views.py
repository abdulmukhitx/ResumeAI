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
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                # Don't use session login anymore - redirect to JWT login instead
                messages.success(request, 'Account created successfully! Please log in with your new account.')
                return redirect('login')
            except IntegrityError as e:
                # Handle database integrity errors gracefully
                if 'username' in str(e).lower():
                    messages.error(request, 'An account with this email already exists. Please try logging in instead.')
                elif 'email' in str(e).lower():
                    messages.error(request, 'An account with this email already exists. Please try logging in instead.')
                else:
                    messages.error(request, 'There was an error creating your account. Please try again.')
        else:
            # Form validation errors will be shown in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

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
    JWT login page - the new default authentication method
    """
    # No need to check session authentication here - JWT handles its own state
    form = UserLoginForm()
    return render(request, 'registration/jwt_login.html', {'form': form})

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
