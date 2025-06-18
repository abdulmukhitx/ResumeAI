from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class JobSearch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_searches')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='job_searches')
    
    # Search parameters
    search_query = models.CharField(max_length=255)
    location = models.CharField(max_length=200, blank=True)
    salary_from = models.PositiveIntegerField(null=True, blank=True)
    salary_to = models.PositiveIntegerField(null=True, blank=True)
    experience_level = models.CharField(max_length=50, blank=True)
    
    # Search results
    total_found = models.PositiveIntegerField(default=0)
    jobs_analyzed = models.PositiveIntegerField(default=0)
    matches_found = models.PositiveIntegerField(default=0)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Search'
        verbose_name_plural = 'Job Searches'
    
    def __str__(self):
        user_email = getattr(self.user, 'email', None)
        return f"{user_email or self.user} - {self.search_query}"

class Job(models.Model):
    # Basic job information from HH.ru
    hh_id = models.CharField(max_length=50, unique=True)  # HH.ru job ID
    title = models.CharField(max_length=300)
    company_name = models.CharField(max_length=200)
    company_url = models.URLField(blank=True)
    
    # Job details
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True, default='')
    responsibilities = models.TextField(blank=True, null=True, default='')
    
    # Location and salary
    location = models.CharField(max_length=200)
    salary_from = models.PositiveIntegerField(null=True, blank=True)
    salary_to = models.PositiveIntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='RUB')
    
    # Employment details
    employment_type = models.CharField(max_length=50, blank=True)  # full-time, part-time, etc.
    experience_required = models.CharField(max_length=100, blank=True)
    
    # Skills and requirements (extracted)
    required_skills = models.JSONField(default=list, blank=True)
    optional_skills = models.JSONField(default=list, blank=True)
    
    # URLs and metadata
    hh_url = models.URLField(blank=True, default='')
    published_at = models.DateTimeField(default=timezone.now)
    
    # Our metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    @property
    def salary_range(self):
        if self.salary_from and self.salary_to:
            return f"{self.salary_from:,} - {self.salary_to:,} {self.salary_currency}"
        elif self.salary_from:
            return f"от {self.salary_from:,} {self.salary_currency}"
        elif self.salary_to:
            return f"до {self.salary_to:,} {self.salary_currency}"
        return "Зарплата не указана"
        
    def get_clean_description(self):
        """
        Returns a clean version of the job description with HTML tags removed
        and properly formatted for display
        """
        import html
        import re
        
        if not self.description:
            return ""
            
        # Unescape HTML entities
        value = html.unescape(self.description)
        
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', ' ', value)
        
        # Fix spaces and line breaks
        value = re.sub(r' +', ' ', value)
        value = re.sub(r'\n{3,}', '\n\n', value)
        
        return value.strip()

class JobMatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matches')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='job_matches')
    match_score = models.FloatField(default=0)  # 0-100 percentage score
    match_details = models.JSONField(default=dict, blank=True)  # Detailed breakdown of the match
    
    # Skills matching data
    matching_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-match_score']
        verbose_name = 'Job Match'
        verbose_name_plural = 'Job Matches'
        unique_together = ('job', 'resume')
    
    def __str__(self):
        # Use self.user directly, as JobMatch already has a user ForeignKey
        job_title = getattr(self.job, 'title', str(self.job))
        return f"{self.user} - {job_title} ({self.match_score:.0f}%)"

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('in_review', 'In Review'),
        ('interview', 'Interview'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='job_applications')
    
    match_score = models.FloatField(default=0)
    cover_letter = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_date = models.DateTimeField(default=timezone.now)
    last_status_update = models.DateTimeField(auto_now=True)
    
    # Response tracking
    employer_response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-applied_date']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        unique_together = ('job', 'user')  # A user can only apply once for a specific job
    
    def __str__(self):
        return f"{self.user} - {self.job.title if hasattr(self.job, 'title') else self.job} ({self.status})"
    
    def get_days_since_applied(self):
        """Return the number of days since application was submitted"""
        return (timezone.now() - self.applied_date).days
        
    def get_status_color(self):
        """Return a Bootstrap color class based on status"""
        color_map = {
            'applied': 'primary',
            'in_review': 'info',
            'interview': 'warning',
            'offered': 'success',
            'accepted': 'success',
            'rejected': 'danger',
            'withdrawn': 'secondary',
        }
        return color_map.get(self.status, 'secondary')
    
    def get_status_display(self):
        """Return a formatted display name for the status"""
        for code, name in self.STATUS_CHOICES:
            if code == self.status:
                return name
        return str(self.status).title()