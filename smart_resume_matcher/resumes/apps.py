from django.apps import AppConfig


class ResumesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resumes'
    
    def ready(self):
        # Import any signals or perform app initialization here
        pass
