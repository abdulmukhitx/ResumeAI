# config/celery.py
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('smart_resume_matcher')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'weekly-job-search': {
        'task': 'jobs.tasks.weekly_job_search_for_all_users',
        'schedule': 604800.0,  # Run every week (7 days * 24 hours * 60 minutes * 60 seconds)
    },
}

# config/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
