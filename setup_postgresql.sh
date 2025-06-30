#!/bin/bash

# 🐘 POSTGRESQL DATABASE SETUP SCRIPT
# ===================================

echo "🚀 Setting up PostgreSQL database for Smart Resume Matcher"
echo "=========================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install it first:"
    echo "   Ubuntu/Debian: sudo apt update && sudo apt install postgresql postgresql-contrib"
    echo "   macOS: brew install postgresql"
    echo "   Or download from: https://www.postgresql.org/download/"
    exit 1
fi

echo "✅ PostgreSQL found"

# Check if PostgreSQL service is running
if ! sudo systemctl is-active --quiet postgresql; then
    echo "🔄 Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
fi

echo "✅ PostgreSQL service is running"

# Create database and user
echo "🔧 Setting up database and user..."

# Switch to postgres user and create database
sudo -u postgres psql -c "CREATE DATABASE jobpilot;" 2>/dev/null || echo "Database 'jobpilot' already exists"
sudo -u postgres psql -c "CREATE USER abdulmukhit WITH PASSWORD 'acernitrO5';" 2>/dev/null || echo "User 'abdulmukhit' already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jobpilot TO abdulmukhit;"
sudo -u postgres psql -c "ALTER USER abdulmukhit CREATEDB;" # Allow user to create test databases

echo "✅ Database and user configured"

# Test connection
echo "🔍 Testing database connection..."
if PGPASSWORD=acernitrO5 psql -h localhost -U abdulmukhit -d jobpilot -c "\dt" &>/dev/null; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed. Please check your PostgreSQL configuration."
    exit 1
fi

echo ""
echo "🎯 DATABASE CONFIGURATION:"
echo "=========================="
echo "Database Name: jobpilot"
echo "Username: abdulmukhit"
echo "Password: acernitrO5"
echo "Host: localhost"
echo "Port: 5432"
echo ""

echo "📋 NEXT STEPS:"
echo "=============="
echo "1. Run migrations: python manage.py migrate"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Start the server: python manage.py runserver"
echo ""

echo "🎉 PostgreSQL setup complete!"
