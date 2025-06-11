from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from .fields import SafeImageField

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = SafeImageField(upload_to='profile_pics/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username from required fields since we use email

    def save(self, *args, **kwargs):
        # Ensure username is always set to email to prevent conflicts
        if not self.username or self.username != self.email:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
        
    def get_profile_picture_url(self):
        """Safely get the profile picture URL or return None"""
        try:
            # First check if field exists and is not None
            if self.profile_picture:
                # Try to access name attribute to validate it's a proper file field
                if hasattr(self.profile_picture, 'name'):
                    import os
                    from django.conf import settings
                    # Check if the file actually exists on disk
                    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, self.profile_picture.name)):
                        # File doesn't exist, reset the field
                        self.profile_picture = None
                        self.save(update_fields=['profile_picture'])
                        return None
                    # Finally try to access the URL
                    return self.profile_picture.url
            return None
        except ValueError:
            # Specifically catch the ValueError that occurs when there's no file
            self.profile_picture = None
            self.save(update_fields=['profile_picture'])
            return None
        except Exception:
            # Catch any other exceptions as a fallback
            return None

class UserProfile(models.Model):
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('middle', 'Middle (4-7 years)'),
        ('senior', 'Senior (7+ years)'),
        ('lead', 'Lead/Principal (10+ years)'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full', 'Full-time'),
        ('part', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Job Preferences
    desired_position = models.CharField(max_length=200, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, blank=True)
    employment_types = models.JSONField(default=list, blank=True)  # Multiple employment types
    preferred_locations = models.JSONField(default=list, blank=True)  # Cities/regions
    
    # Salary Preferences
    min_salary = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_salary = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    salary_currency = models.CharField(max_length=10, default='RUB')
    
    # Job Search Settings
    is_job_search_active = models.BooleanField(default=True)
    weekly_job_emails = models.BooleanField(default=True)
    last_job_search = models.DateTimeField(null=True, blank=True)
    
    # Skills (will be extracted from resume)
    skills = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile" if getattr(self, 'user', None) and getattr(self.user, 'email', None) else "No User Profile"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.min_salary and self.max_salary and self.min_salary > self.max_salary:
            raise ValidationError('Minimum salary cannot be greater than maximum salary.')