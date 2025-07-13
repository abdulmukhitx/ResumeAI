# Railway Deployment Configuration Guide

## Custom Build Command Options

### Option 1: Direct Command (Recommended)
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### Option 2: Using Build Script
```bash
chmod +x railway_build.sh && ./railway_build.sh
```

### Option 3: Comprehensive Build
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput --clear && python manage.py check --deploy
```

## Railway Environment Variables

Set these variables in your Railway dashboard:

### Required Variables
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings
```

### Optional Variables
```
ALLOWED_HOSTS=your-domain.railway.app
GROQ_API_KEY=your-groq-api-key
HH_API_USER_AGENT=Smart Resume Matcher (your-email@example.com)
```

## Railway Service Configuration

### 1. Web Service
- **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
- **Build Command**: Use one of the options above
- **Port**: Railway will automatically set the PORT environment variable

### 2. Database (Optional)
- **Type**: PostgreSQL (if you want to upgrade from SQLite later)
- **Connection**: Railway will provide DATABASE_URL automatically

## Deployment Steps

### 1. Connect Repository
1. Go to Railway dashboard
2. Create new project
3. Connect your GitHub repository
4. Select the main branch

### 2. Configure Build
1. Go to your service settings
2. Add the Custom Build Command (Option 1 recommended)
3. Set the Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120`

### 3. Set Environment Variables
Add the required environment variables listed above.

### 4. Deploy
Railway will automatically deploy when you push to the main branch.

## Current File Structure

```
smart_resume_matcher/
├── requirements.txt          # Python dependencies (SQLite version)
├── Procfile                 # Process configuration
├── start.sh                 # Start script with migrations
├── railway_build.sh         # Custom build script
├── runtime.txt              # Python version (3.11.0)
├── config/
│   └── settings.py          # Django settings (Railway-optimized)
└── staticfiles/             # Static files (auto-generated)
```

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that requirements.txt is valid
2. **Static Files Missing**: Ensure collectstatic runs in build command
3. **Database Issues**: SQLite should work fine for initial deployment
4. **Port Issues**: Railway sets PORT automatically, don't hardcode it

### Logs
Check Railway logs in the dashboard for deployment issues.

## Testing Before Deployment

Run this locally to test:
```bash
./test_railway_deployment.sh
```

## Admin Access

After deployment:
- **URL**: `https://your-app.railway.app/admin/`
- **Username**: `admin@example.com`
- **Password**: `admin123`

**Important**: Change these credentials after first login!

## Next Steps After Deployment

1. **Test the deployment**: Visit your Railway URL
2. **Check admin access**: Login to `/admin/`
3. **Test JWT authentication**: Try the login functionality
4. **Monitor logs**: Check for any runtime errors
5. **Set up custom domain** (optional): Add your own domain in Railway settings

## Upgrade Path

Once the basic deployment works, you can:
1. Add PostgreSQL database
2. Add file upload capabilities
3. Add AI features with proper API keys
4. Add background task processing with Celery + Redis

This configuration provides a minimal, working deployment that can be extended later.
