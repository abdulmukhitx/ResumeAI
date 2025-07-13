#!/bin/bash

# Railway Deployment Script
echo "🚀 Deploying Smart Resume Matcher to Railway"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the project root."
    exit 1
fi

# Switch to minimal requirements for deployment
echo "📦 Switching to minimal requirements..."
if [ -f "requirements_minimal.txt" ]; then
    cp requirements_minimal.txt requirements.txt
    echo "✅ Using minimal requirements for deployment"
else
    echo "⚠️  Minimal requirements not found, using current requirements.txt"
fi

# Make sure all scripts are executable
chmod +x build.sh
chmod +x start.sh

# Add all changes to git
echo "📝 Adding changes to git..."
git add .

# Commit changes
echo "💾 Committing deployment fixes..."
git commit -m "Fix Railway deployment: minimal requirements, proper build/start scripts, Railway-specific settings"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Go to your Railway dashboard"
echo "2. Redeploy the service"
echo "3. Check the logs for any remaining issues"
echo "4. Set environment variables:"
echo "   - SECRET_KEY (generate a new one)"
echo "   - DATABASE_URL (PostgreSQL connection string)"
echo "   - DEBUG=False"
echo "   - GROQ_API_KEY (if using AI features)"
echo ""
echo "🎯 Railway deployment should now work correctly!"
