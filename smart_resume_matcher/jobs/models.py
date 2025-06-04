from django.db import models
from django.contrib.auth import get_user_model

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
        return f"{self.user.email} - {self.search_query}"

class Job(models.Model):
    # Basic job information from HH.ru
    hh_id = models.CharField(max_length=50, unique=True)  # HH.ru job ID
    title = models.CharField(max_length=300)
    company_name = models.CharField(max_length=200)
    company_url = models.URLField(blank=True)
    
    # Job details
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    
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
    hh_url = models.URLField()
    published_at = models.DateTimeField()
    
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

class JobMatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matches')
    resume = models.ForeignKey('resumes.Resume', on_delete=models.CASCADE, related_name='job_matches')
    job_search = models.ForeignKey(JobSearch, on_delete=models.CASCADE, related_name='matches')
    
    # Matching scores
    overall_score = models.FloatField()  # 0.0 to 1.0
    skills_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    title_score = models.FloatField(default=0.0)
    location_score = models.FloatField(default=0.0)
    salary_score = models.FloatField(default=0.0)
    
    # Matching details
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    match_explanation = models.TextField(blank=True)
    
    # User interaction
    is_viewed = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-overall_score', '-created_at']
        unique_together = ['user', 'job', 'resume']
        verbose_name = 'Job Match'
        verbose_name_plural = 'Job Matches'
    
    def __str__(self):
        return f"{self.user.email} - {self.job.title} ({self.overall_score:.2f})"
    
    @property
    def match_percentage(self):
        return round(self.overall_score * 100, 1)