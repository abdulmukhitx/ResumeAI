# Deployment Guide for Smart Resume Matcher on Render

This guide will help you deploy the Smart Resume Matcher application on Render.

## Prerequisites

1. A [Render](https://render.com/) account
2. Your application code in a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Setup Your Repository

Make sure your repository includes these files:
- `requirements.txt` - Contains all Python dependencies
- `Procfile` - Specifies the commands to run
- `build.sh` - Build script to set up the application
- `render.yaml` - Blueprint for Render services

## Step 2: Deploy Using the Dashboard

### Web Service Setup

1. Log in to your Render account
2. Go to Dashboard > New > Web Service
3. Connect your repository
4. Configure the service:
   - **Name**: smart-resume-matcher
   - **Environment**: Python
   - **Region**: Choose the closest to your users
   - **Branch**: main (or your preferred branch)
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
   - **Plans**: Choose Free or Standard based on your needs

5. Add the following environment variables:
   - `SECRET_KEY`: A secure random string
   - `DEBUG`: false
   - `ALLOWED_HOSTS`: Your app's domain, e.g., `your-app.onrender.com`
   - `GROQ_API_KEY`: Your AI service API key
   - `EMAIL_HOST_USER`: Your email address
   - `EMAIL_HOST_PASSWORD`: Your email password

6. Click "Create Web Service"

### Database Setup

1. Go to Dashboard > New > PostgreSQL
2. Configure your database:
   - **Name**: smart-resume-matcher-db
   - **Database**: postgres
   - **User**: postgres
   - **Region**: Same as your web service
   - **Plan**: Free or Standard

3. After creation, get the External Database URL
4. Add it as `DATABASE_URL` environment variable to your web service

### Redis Setup

1. Go to Dashboard > New > Redis
2. Configure your Redis instance:
   - **Name**: smart-resume-redis
   - **Region**: Same as your web service
   - **Plan**: Free or Standard

3. After creation, get the Redis URL
4. Add it as `REDIS_URL` environment variable to your web service

### Celery Worker Setup

1. Go to Dashboard > New > Web Service
2. Connect the same repository
3. Configure the service:
   - **Name**: smart-resume-celery-worker
   - **Environment**: Python
   - **Region**: Same as your web service
   - **Branch**: Same as your web service
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A config worker --loglevel=info`
   - **Plans**: Free or Standard

4. Add the same environment variables as the web service
5. Click "Create Web Service"

### Celery Beat Setup

1. Go to Dashboard > New > Web Service
2. Connect the same repository
3. Configure the service:
   - **Name**: smart-resume-celery-beat
   - **Environment**: Python
   - **Region**: Same as your web service
   - **Branch**: Same as your web service
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A config beat --loglevel=info`
   - **Plans**: Free or Standard

4. Add the same environment variables as the web service
5. Click "Create Web Service"

## Step 3: Verify Deployment

1. Wait for all services to deploy (may take a few minutes)
2. Visit your application at `https://your-app.onrender.com`
3. Check the logs for any errors

## Step 4: Setup a Custom Domain (Optional)

1. Go to your Web Service > Settings > Custom Domain
2. Follow the instructions to add your domain

## Troubleshooting

- Check the logs for each service for error messages
- Ensure all environment variables are set correctly
- Make sure your DATABASE_URL and REDIS_URL are correct
- Check that your application is configured to use the correct database settings
- Verify that static files are being served correctly
