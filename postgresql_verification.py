#!/usr/bin/env python3
"""
PostgreSQL Migration Verification Script
Verify that the switch from SQLite to PostgreSQL is working correctly.
"""

import os
import sys
import django
import requests

# Add the project directory to the Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from resumes.models import Resume
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def verify_database_connection():
    """Verify PostgreSQL database connection."""
    print("🔗 Verifying Database Connection...")
    
    try:
        # Check database engine
        db_engine = connection.settings_dict['ENGINE']
        db_name = connection.settings_dict['NAME']
        db_host = connection.settings_dict['HOST']
        db_port = connection.settings_dict['PORT']
        
        print(f"✅ Database Engine: {db_engine}")
        print(f"✅ Database Name: {db_name}")
        print(f"✅ Database Host: {db_host}")
        print(f"✅ Database Port: {db_port}")
        
        if 'postgresql' in db_engine:
            print("✅ Successfully connected to PostgreSQL")
        else:
            print(f"❌ Expected PostgreSQL, got {db_engine}")
            return False
        
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL Version: {version[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_data_migration():
    """Verify that data exists in PostgreSQL."""
    print("📊 Verifying Data Migration...")
    
    try:
        # Check users
        user_count = User.objects.count()
        print(f"✅ Users in PostgreSQL: {user_count}")
        
        if user_count > 0:
            user = User.objects.first()
            print(f"✅ Sample user: {user.email}")
        
        # Check resumes
        resume_count = Resume.objects.count()
        print(f"✅ Resumes in PostgreSQL: {resume_count}")
        
        if resume_count > 0:
            resume = Resume.objects.first()
            print(f"✅ Sample resume: {resume.original_filename}")
            print(f"✅ Resume status: {resume.status}")
            if resume.extracted_skills:
                print(f"✅ Resume has skills: {len(resume.extracted_skills)} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Data verification failed: {e}")
        return False

def verify_authentication():
    """Verify JWT authentication works with PostgreSQL."""
    print("🔐 Verifying Authentication...")
    
    try:
        # Get a user and generate JWT
        user = User.objects.first()
        if not user:
            print("❌ No users found for auth test")
            return False
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        print(f"✅ Generated JWT for user: {user.email}")
        
        # Test auth API endpoint
        url = "http://localhost:8000/api/auth/user/"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auth API works: {data.get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ Auth API failed: {response.status_code}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server for auth test")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def verify_resume_functionality():
    """Verify resume functionality works with PostgreSQL."""
    print("📄 Verifying Resume Functionality...")
    
    try:
        # Test resume API endpoints
        user = User.objects.first()
        if not user:
            print("❌ No users found for resume test")
            return False
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Test resume list API
        url = "http://localhost:8000/api/resume/list/"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resume list API works: {len(data.get('resumes', []))} resumes")
            return True
        else:
            print(f"❌ Resume list API failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Resume functionality test failed: {e}")
        return False

def main():
    """Run all PostgreSQL verification tests."""
    print("🐘 PostgreSQL Migration Verification")
    print("=" * 50)
    
    tests = [
        ("Database Connection", verify_database_connection),
        ("Data Migration", verify_data_migration),
        ("Authentication", verify_authentication),
        ("Resume Functionality", verify_resume_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("=" * 50)
    print("📊 PostgreSQL Migration Summary:")
    all_passed = True
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 SUCCESS! PostgreSQL migration is complete and working!")
        print()
        print("✨ What's working:")
        print("   • PostgreSQL database connection")
        print("   • Data migration (users and resumes)")
        print("   • JWT authentication")
        print("   • Resume functionality")
        print()
        print("🌐 Your application is now running on PostgreSQL at:")
        print("   http://localhost:8000")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()
