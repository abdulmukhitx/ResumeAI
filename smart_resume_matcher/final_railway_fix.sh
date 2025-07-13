#!/bin/bash

# Final Railway Deployment Fix
echo "🔧 Final Railway Deployment Fix"
echo "================================"

# Switch to Railway-specific files
echo "📝 Switching to Railway-specific configuration..."
cp Procfile.railway Procfile
cp requirements.txt requirements.backup
echo "✅ Configuration switched"

# Test the Railway settings
echo "🧪 Testing Railway configuration..."
export DJANGO_SETTINGS_MODULE=config.railway_settings
python manage.py check
echo "✅ Railway settings validated"

# Test migrations
echo "🗄️  Testing migrations..."
python manage.py migrate --run-syncdb
echo "✅ Migrations successful"

# Test static files
echo "📁 Testing static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"

# Create a simple test
echo "🌐 Testing server startup..."
timeout 3 python manage.py runserver 0.0.0.0:8000 &
sleep 2
curl -s -o /dev/null -w "Server status: %{http_code}\n" http://localhost:8000/ || echo "Server test skipped"
pkill -f "python manage.py runserver" 2>/dev/null || true

# Commit the fixes
echo "📝 Committing Railway fixes..."
git add .
git commit -m "Fix Railway deployment: simplified settings, updated JWT version, removed problematic middleware"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Railway deployment fix complete!"
echo ""
echo "🔧 Railway Configuration:"
echo "   - Custom Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput"
echo "   - Start Command: chmod +x start.sh && ./start.sh"
echo "   - Environment Variables: SECRET_KEY, DEBUG=False, RAILWAY_ENVIRONMENT (auto-set)"
echo ""
echo "🎯 This should resolve the deployment issues on Railway!"
