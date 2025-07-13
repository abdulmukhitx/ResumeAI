# Railway PostgreSQL Database Deployment Guide

## Your Application is Already PostgreSQL Ready! ✅

Your Django app is already configured to use PostgreSQL when the `DATABASE_URL` environment variable is provided.

## Railway Deployment Steps:

### 1. Create PostgreSQL Service on Railway
From your Railway screenshot, I can see you already have a PostgreSQL service. Use these connection details:

**Connection URL Pattern:**
```
postgresql://[username]:[password]@[host]:[port]/[database]
```

### 2. Set Environment Variables in Railway

Add these environment variables to your Railway project:

**Required Database Variables:**
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@metro.proxy.rlwy.net:17430/railway
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[your-generated-password]
POSTGRES_HOST=metro.proxy.rlwy.net
POSTGRES_PORT=17430
```

**Application Variables:**
```bash
DEBUG=False
SECRET_KEY=[generate-a-new-secret-key]
ALLOWED_HOSTS=*.railway.app,*.up.railway.app
GROQ_API_KEY=[your-groq-api-key]
DJANGO_SETTINGS_MODULE=config.settings
```

### 3. Migration Commands for Railway

Add these to your Railway service build commands:

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(email='admin@admin.com').exists():
    User.objects.create_superuser('admin@admin.com', 'adminpass123')
    print('Superuser created')
"
```

### 4. Required Files for Deployment

Your app already has:
- ✅ `requirements.txt` 
- ✅ `Procfile`
- ✅ PostgreSQL configuration
- ✅ Static files configuration

## Database Migration Strategy:

### Option A: Fresh Database (Recommended)
1. Use the Railway PostgreSQL service
2. Run migrations to create fresh tables
3. Create a new superuser account

### Option B: Data Migration from SQLite
If you want to keep your existing data:

1. Export data from SQLite:
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > datadump.json
```

2. Load data to PostgreSQL:
```bash
python manage.py loaddata datadump.json
```

## Quick Deployment Commands:

```bash
# 1. Install PostgreSQL adapter
pip install psycopg2-binary

# 2. Update requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt

# 3. Test locally with PostgreSQL
export DATABASE_URL="postgresql://postgres:password@localhost:5432/resumeai"
python manage.py migrate
python manage.py runserver

# 4. Deploy to Railway
git add .
git commit -m "Add PostgreSQL deployment configuration"
git push origin main
```

## Your Connection String (from screenshot):
```
postgresql://postgres:********@metro.proxy.rlwy.net:17430/railway
```

## Next Steps:
1. ✅ PostgreSQL service is already created
2. 🔄 Set environment variables in Railway dashboard
3. 🔄 Deploy your application
4. 🔄 Run migrations
5. 🔄 Create superuser account

Your app is ready for PostgreSQL deployment! 🚀
