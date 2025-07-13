#!/bin/bash
# Simple Railway deployment without PostgreSQL

set -e

echo "🚀 Simple Railway Deployment (SQLite)"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Use SQLite-compatible requirements
echo "📦 Switching to SQLite requirements..."
cp requirements_sqlite.txt requirements.txt

# Update settings for SQLite deployment
echo "⚙️  Updating settings for SQLite deployment..."
cat > railway_settings.py << 'EOF'
# Railway-specific settings for SQLite deployment
import os
from pathlib import Path
from datetime import timedelta

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='railway-dev-key-change-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)

# Railway environment detection
RAILWAY_ENVIRONMENT = config('RAILWAY_ENVIRONMENT', default=None)
IS_RAILWAY = RAILWAY_ENVIRONMENT is not None

# Allowed hosts configuration
ALLOWED_HOSTS = ['*']  # Railway handles the routing

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

LOCAL_APPS = [
    'accounts',
    'resumes',
    'jobs',
    'notifications',
    'core',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.JWTAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - SQLite for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,  # Simplified for SQLite
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins for Railway

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
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
    },
}

# Dummy settings for features that need external dependencies
GROQ_API_KEY = config('GROQ_API_KEY', default='dummy-key')
GROQ_API_URL = config('GROQ_API_URL', default='https://api.groq.com/openai/v1/chat/completions')
HH_API_BASE_URL = config('HH_API_BASE_URL', default='https://api.hh.ru')
HH_API_USER_AGENT = config('HH_API_USER_AGENT', default='Smart Resume Matcher (contact@example.com)')
EOF

# Copy the simple settings
cp railway_settings.py config/settings.py

# Update Procfile for simple deployment
cat > Procfile << 'EOF'
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
EOF

# Update start script
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting Smart Resume Matcher (SQLite)..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=config.settings

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if needed
echo "Creating superuser if needed..."
python manage.py shell << SHELL_EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created: admin@example.com / admin123')
else:
    print('Superuser already exists')
SHELL_EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo "Starting gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
EOF

chmod +x start.sh

# Test deployment locally
echo "🧪 Testing deployment locally..."
python manage.py check
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput

# Add all changes to git
echo "📝 Adding changes to git..."
git add .

# Commit changes
echo "💾 Committing simple deployment..."
git commit -m "Simple Railway deployment with SQLite - no external dependencies"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Simple deployment ready!"
echo ""
echo "🎯 This deployment should work on Railway without any external dependencies."
echo "   Set these environment variables in Railway:"
echo "   - SECRET_KEY (generate a new one)"
echo "   - DEBUG=False"
echo ""
echo "🔧 Admin credentials: admin@example.com / admin123"
