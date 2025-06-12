
# Production deployment settings
import os
from .settings import *

# Override for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Update with actual domain

# Database persistence for Render
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600)

# Static files for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'resumes': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
