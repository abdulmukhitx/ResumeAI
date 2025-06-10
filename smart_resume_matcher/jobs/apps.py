from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'
    
    def ready(self):
        # Placeholder for future signal handlers
        # If you add a signals.py file, uncomment the line below
        # import jobs.signals  # noqa
        pass
