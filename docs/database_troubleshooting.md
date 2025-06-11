# Database Troubleshooting Guide for Render Deployment

This document provides detailed guidance for resolving database connection issues when deploying the Smart Resume Matcher application on Render.com.

## Common Database Issues

### 1. Connection Errors During Build

**Symptoms:**
- Error messages like "could not connect to server: Connection refused"
- Build process fails when trying to run migrations

**Potential Causes:**
- Database hasn't fully initialized before migrations attempt to run
- Database credentials are incorrect
- Database service is not properly provisioned

**Solutions:**
- Our updated `build.sh` now includes:
  - A delay to allow the database to initialize
  - A connection test before running migrations
  - Error handling to continue the build even if migrations fail
  - Retry logic during application startup

### 2. "NoneType has no attribute 'get'" Errors

**Symptoms:**
- Application crashes with "'NoneType' object has no attribute 'get'"
- Database operations fail after the application starts

**Potential Causes:**
- Database connection was established but later dropped
- Connection pool exhaustion
- Incorrect environment configuration

**Solutions:**
- Our updated `settings.py` now includes:
  - Connection pooling configuration
  - Timeout settings
  - SSL mode configuration
  - Atomic requests to improve transaction handling

### 3. Missing Database Tables

**Symptoms:**
- "Table does not exist" errors
- Application can't find models that should exist

**Potential Causes:**
- Migrations didn't run successfully
- Database was reset but migrations weren't re-run

**Solutions:**
- Our `start.sh` script runs migrations on startup
- You can manually run migrations by connecting to the Render shell:
  ```
  cd smart_resume_matcher
  python manage.py migrate
  ```

## Verifying Database Connection

To verify your database connection is working properly:

1. SSH into your Render service shell
2. Connect to the Django shell:
   ```
   cd smart_resume_matcher
   python manage.py shell
   ```
3. Test the database connection:
   ```python
   from django.db import connections
   cursor = connections['default'].cursor()
   cursor.execute("SELECT 1")
   result = cursor.fetchone()
   print(result)
   ```

This should print `(1,)` if the connection is successful.

## Checking Database Logs

If you're encountering persistent database issues:

1. Go to your Render dashboard
2. Navigate to the "smart-resume-matcher-db" service
3. Check the logs for any relevant error messages

## Database Backup and Restore

If you need to reset your database:

1. Back up your data first:
   ```
   cd smart_resume_matcher
   python manage.py dumpdata > backup.json
   ```

2. After fixing issues, restore data if needed:
   ```
   python manage.py loaddata backup.json
   ```

## Database Connection Configuration

Our updated database configuration in `settings.py` includes:

```python
DATABASES = {
    'default': {
        # Local SQLite for development
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Use PostgreSQL on Render
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Parse database URL with options for more reliable connections
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)
    
    # Add connection pooling and more robust error handling
    DATABASES['default']['CONN_MAX_AGE'] = 60
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'sslmode': 'require',  # Required for Render
    }
    
    # Add retries for database operations
    DATABASES['default']['ATOMIC_REQUESTS'] = True
```

This configuration helps ensure more reliable database connections in the production environment.
