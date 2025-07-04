"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)
from accounts.jwt_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view as jwt_logout_view,
    user_profile_view,
    verify_token_view,
)
from accounts.api_views import register_api_view
from core.views import home_view
from accounts.views import register_view, login_view, logout_view, profile_view, edit_profile_view, jwt_login_view, jwt_demo_view
from accounts.jwt_compatible_views import jwt_profile_view, jwt_home_view, jwt_resume_upload_view
from resumes.views import resume_upload_view
from resumes.ultra_safe_api import ultra_safe_resume_upload, ultra_safe_resume_status, ultra_safe_resume_list

# Simple handler for Chrome DevTools requests
def chrome_devtools_handler(request):
    return HttpResponse('{}', content_type='application/json')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('', home_view, name='home'),
    
    # Authentication URLs
    path('register/', register_view, name='register'),
    path('login/', jwt_login_view, name='login'),  # JWT is now default
    path('session-login/', login_view, name='session_login'),  # Keep legacy for migration
    path('jwt-demo/', jwt_demo_view, name='jwt_demo'),
    path('jwt-test/', lambda request: render(request, 'jwt_test.html'), name='jwt_test'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # User Profile URLs
    path('profile/', profile_view, name='profile'),  # Session-based fallback
    path('jwt-profile/', jwt_profile_view, name='jwt_profile'),  # JWT-only profile
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    
    # Resume URLs
    path('resume/upload/', resume_upload_view, name='resume_upload'),  # Session-based fallback
    path('jwt-resume-upload/', jwt_resume_upload_view, name='jwt_resume_upload'),  # JWT-only resume upload
    
    # Job URLs
    path('jobs/', include('jobs.urls')),
    
    # JWT API URLs
    path('api/auth/register/', register_api_view, name='api_register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='jwt_api_login'),  # JWT Login API
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/logout/', jwt_logout_view, name='jwt_logout'),
    path('api/auth/user/', user_profile_view, name='jwt_user_profile'),
    path('api/auth/verify/', verify_token_view, name='jwt_verify_user'),
    
    # Resume API URLs
    path('api/resume/upload/', ultra_safe_resume_upload, name='api_resume_upload'),
    path('api/resume/status/<int:resume_id>/', ultra_safe_resume_status, name='api_resume_status'),
    path('api/resume/list/', ultra_safe_resume_list, name='api_resume_list'),
    
    # Chrome DevTools handler (suppress 404 errors)
    path('.well-known/appspecific/com.chrome.devtools.json', chrome_devtools_handler),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
