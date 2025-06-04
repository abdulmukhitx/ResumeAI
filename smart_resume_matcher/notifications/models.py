from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailNotification(models.Model):
    TYPE_CHOICES = [
        ('welcome', 'Welcome Email'),
        ('resume_analyzed', 'Resume Analysis Complete'),
        ('job_matches', 'New Job Matches'),
        ('weekly_digest', 'Weekly Job Digest'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_notifications')
    email_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    
    # Email content
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Related objects (optional)
    job_search_id = models.PositiveIntegerField(null=True, blank=True)
    resume_id = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'
    
    def __str__(self):
        return f"{self.user.email} - {self.email_type} - {self.status}"