# Render Deployment Guide

This document provides guidance for deploying the Smart Resume Matcher application on Render.com.

## Project Structure

The project has a nested structure:
- Root directory: Contains the main configuration files for deployment
- `smart_resume_matcher/`: Contains the actual Django application code

## Deployment Configuration

### Render.yaml

The `render.yaml` file at the root directory defines all services:
- Web service: The main Django application
- Celery worker: For background task processing
- Celery beat: For scheduled tasks
- Redis service: For message queueing
- PostgreSQL database: For data storage

### Build Process

The deployment uses `build.sh` which:
1. Detects the correct directory structure
2. Installs dependencies
3. Collects static files
4. Tests database connectivity
5. Runs migrations if possible

### Start Process

The `start.sh` script:
1. Ensures we're in the correct directory
2. Runs any pending migrations
3. Starts the gunicorn server

## Troubleshooting

### Database Connection Issues

If you see database connection errors during deployment:

1. Check if the database is properly provisioned on Render
2. Verify that the DATABASE_URL environment variable is correctly set
3. The build process includes a 5-second delay to allow the database to initialize fully
4. Failed migrations during build will be retried during application startup

### Static Files

If static files are not working:
1. Make sure `whitenoise` is properly configured in settings.py
2. Verify that collectstatic runs without errors during build

### Worker Services

If Celery workers are not starting:
1. Check Redis connection
2. Verify that the worker commands have the correct path to the Django project

## Common Commands

To manually run migrations:
```
python manage.py migrate
```

To manually collect static files:
```
python manage.py collectstatic --no-input
```

To create a superuser:
```
python manage.py createsuperuser
```

## Environment Variables

Key environment variables required for proper operation:
- DATABASE_URL: PostgreSQL database connection string
- REDIS_URL: Redis connection string
- SECRET_KEY: Django secret key
- DEBUG: Set to false in production
- ALLOWED_HOSTS: Set to include your Render domain

These are automatically set by the render.yaml configuration.
