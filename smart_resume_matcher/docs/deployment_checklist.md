# Render Deployment Checklist

## Pre-Deployment
- [ ] All dependencies are listed in requirements.txt
- [ ] build.sh is executable (chmod +x build.sh)
- [ ] Procfile is correctly configured
- [ ] render.yaml blueprint is up to date
- [ ] .env.example contains all required environment variables
- [ ] DEBUG is set to False in production
- [ ] ALLOWED_HOSTS includes your Render domain
- [ ] Database migrations are prepared
- [ ] Static files configuration is correct (using Whitenoise)

## Environment Variables to Set in Render
- [ ] SECRET_KEY (generate a secure random string)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS=your-app.onrender.com
- [ ] GROQ_API_KEY (your AI service API key)
- [ ] EMAIL_HOST_USER (your email for sending notifications)
- [ ] EMAIL_HOST_PASSWORD (your email password or app password)
- [ ] HH_API_USER_AGENT (user agent for HH.ru API)

## Database and Redis
- [ ] PostgreSQL database is created in Render
- [ ] DATABASE_URL is added to environment variables
- [ ] Redis instance is created in Render
- [ ] REDIS_URL is added to environment variables

## Celery Workers
- [ ] Celery worker service is configured correctly
- [ ] Celery beat service is configured correctly
- [ ] Both services have the same environment variables as the main web service

## Post-Deployment
- [ ] Visit the application URL to verify it's working
- [ ] Check the logs for any errors
- [ ] Test user registration and login
- [ ] Test resume upload functionality
- [ ] Test job search functionality
- [ ] Test job application process

## Performance and Security
- [ ] Static files are being served correctly
- [ ] Media files are being stored and served correctly
- [ ] HTTPS is enabled
- [ ] Database backups are configured (if needed)
- [ ] Application performance is acceptable
