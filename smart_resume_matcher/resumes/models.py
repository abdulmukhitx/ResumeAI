import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()

def resume_upload_path(instance, filename):
    return f'resumes/{instance.user.id}/{filename}'

class Resume(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Analysis Completed'),
        ('completed_with_warnings', 'Completed with Warnings'),
        ('failed', 'Analysis Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text='Only PDF files are allowed'
    )
    original_filename = models.CharField(max_length=255)
    
    # Analysis status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    analysis_started_at = models.DateTimeField(null=True, blank=True)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    has_extraction_issues = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    error_type = models.CharField(max_length=50, blank=True)
    warning_message = models.TextField(blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    
    # Extracted content
    raw_text = models.TextField(blank=True)
    
    # AI Analysis Results
    extracted_skills = models.JSONField(default=list, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    job_titles = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)
    
    # Analysis summary
    analysis_summary = models.TextField(blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    # Metadata
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Resume'
        verbose_name_plural = 'Resumes'
        
    def __str__(self):
        user_email = getattr(self.user, 'email', str(self.user))
        return f"{user_email} - {self.original_filename}"
    
    def save(self, *args, **kwargs):
        if self.file:
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
            if not self.original_filename:
                self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
    
    @property
    def analysis_duration(self):
        if self.analysis_started_at and self.analysis_completed_at:
            return self.analysis_completed_at - self.analysis_started_at
        return None