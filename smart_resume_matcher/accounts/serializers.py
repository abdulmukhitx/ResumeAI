"""
Custom JWT serializers for enhanced token responses
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that includes user information in the token response
    Uses email field instead of username since our model uses email as USERNAME_FIELD
    """
    
    # Add an email field for authentication
    email = serializers.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the username field as we use email
        if 'username' in self.fields:
            del self.fields['username']
    
    def validate(self, attrs):
        """
        Override validate to handle email authentication and add user information
        """
        # Get email and password from request
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authenticate using email as username
            from django.contrib.auth import authenticate
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if user is None:
                raise serializers.ValidationError('No active account found with the given credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            # Create tokens
            refresh = self.get_token(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            # Add user information to the response
            data.update({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                }
            })
            
            # Add user profile information if it exists
            if hasattr(user, 'profile'):
                profile = user.profile
                data['user']['profile'] = {
                    'first_name': profile.first_name,
                    'last_name': profile.last_name,
                    'phone': profile.phone,
                    'location': profile.location,
                    'desired_position': profile.desired_position,
                    'experience_level': profile.experience_level,
                    'employment_types': profile.employment_types,
                    'preferred_locations': profile.preferred_locations,
                    'min_salary': profile.min_salary,
                    'max_salary': profile.max_salary,
                    'salary_currency': profile.salary_currency,
                    'is_job_search_active': profile.is_job_search_active,
                    'skills': profile.skills,
                    'full_name': profile.full_name,
                }
            
            # Add latest resume information if it exists
            if hasattr(user, 'resumes'):
                latest_resume = user.resumes.filter(status='completed').first()
                if latest_resume:
                    data['user']['latest_resume'] = {
                        'id': latest_resume.id,
                        'filename': latest_resume.original_filename,
                        'uploaded_at': latest_resume.created_at.isoformat(),
                        'skills_count': len(latest_resume.extracted_skills),
                        'experience_level': latest_resume.experience_level,
                        'status': latest_resume.status,
                    }
            
            # Update last login
            from django.contrib.auth import update_session_auth_hash
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return data
        
        raise serializers.ValidationError('Must include "email" and "password"')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information in API responses
    """
    profile = serializers.SerializerMethodField()
    latest_resume = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'is_staff', 'is_active', 'date_joined', 'last_login',
            'profile', 'latest_resume'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        """Get user profile information"""
        if hasattr(obj, 'profile'):
            profile = obj.profile
            return {
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'phone': profile.phone,
                'location': profile.location,
                'desired_position': profile.desired_position,
                'experience_level': profile.experience_level,
                'employment_types': profile.employment_types,
                'preferred_locations': profile.preferred_locations,
                'min_salary': profile.min_salary,
                'max_salary': profile.max_salary,
                'salary_currency': profile.salary_currency,
                'is_job_search_active': profile.is_job_search_active,
                'skills': profile.skills,
                'full_name': profile.full_name,
            }
        return None
    
    def get_latest_resume(self, obj):
        """Get latest resume information"""
        if hasattr(obj, 'resumes'):
            latest_resume = obj.resumes.filter(status='completed').first()
            if latest_resume:
                return {
                    'id': latest_resume.id,
                    'filename': latest_resume.original_filename,
                    'uploaded_at': latest_resume.created_at.isoformat(),
                    'skills_count': len(latest_resume.extracted_skills),
                    'experience_level': latest_resume.experience_level,
                    'status': latest_resume.status,
                }
        return None
