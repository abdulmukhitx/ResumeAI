"""
Custom JWT serializers for enhanced token responses
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that includes user information in the token response
    """
    
    @classmethod
    def get_token(cls, user):
        """
        Add custom claims to the JWT token payload
        """
        token = super().get_token(user)
        
        # Add custom claims to the token payload
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        
        return token
    
    def validate(self, attrs):
        """
        Override validate to add user information to the response
        """
        data = super().validate(attrs)
        
        # Add user information to the response
        user = self.user
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
        
        return data


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
