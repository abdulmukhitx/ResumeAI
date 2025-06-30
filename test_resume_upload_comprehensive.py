#!/usr/bin/env python3
"""
Comprehensive Resume Upload Test
Tests the entire upload flow from API call to database storage and analysis
"""
import os
import sys
import requests
import json
import time
from io import BytesIO

# Add Django project to path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from accounts.models import User
from resumes.models import Resume
from django.db import connection

def create_test_pdf():
    """Create a simple test PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "John Doe")
        p.drawString(100, 730, "Software Engineer")
        p.drawString(100, 710, "Experience: 5 years in Python development")
        p.drawString(100, 690, "Skills: Python, Django, JavaScript, React")
        p.drawString(100, 670, "Education: Computer Science Degree")
        p.save()
        return buffer.getvalue()
    except ImportError:
        # Fallback: create a simple text file
        return b"John Doe\nSoftware Engineer\nExperience: 5 years in Python development\nSkills: Python, Django, JavaScript, React\nEducation: Computer Science Degree"

def test_user_creation_and_login():
    """Test user creation and JWT token generation"""
    print("=== Testing User Creation and Login ===")
    
    # Create test user
    import random
    random_id = random.randint(1000, 9999)
    username = f"testuser_upload_{random_id}"
    email = f"testuser_{random_id}@example.com"
    password = "testpass123"
    
    # Delete existing user if exists
    User.objects.filter(username=username).delete()
    
    # Register user
    register_data = {
        'username': username,
        'email': email,
        'password': password,
        'password2': password
    }
    
    response = requests.post('http://localhost:8001/api/auth/register/', json=register_data)
    print(f"Registration response: {response.status_code}")
    if response.status_code != 201:
        print(f"Registration failed: {response.text}")
        return None
    
    # Login to get token
    login_data = {
        'email': email,
        'password': password
    }
    
    response = requests.post('http://localhost:8001/api/auth/login/', json=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
    
    token_data = response.json()
    print(f"Login successful: {token_data}")
    return token_data.get('access')

def test_resume_upload(token):
    """Test resume upload with proper authentication"""
    print("\n=== Testing Resume Upload ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    # Create test file
    pdf_content = create_test_pdf()
    
    files = {
        'file': ('test_resume.pdf', pdf_content, 'application/pdf')
    }
    
    data = {
        'job_description': 'We are looking for a Python developer with Django experience'
    }
    
    print("Uploading resume...")
    response = requests.post('http://localhost:8001/api/resume/upload/', 
                           headers=headers, files=files, data=data)
    
    print(f"Upload response status: {response.status_code}")
    print(f"Upload response: {response.text}")
    
    if response.status_code in [200, 201]:
        try:
            result = response.json()
            print(f"Upload successful: {result}")
            return result
        except json.JSONDecodeError:
            print("Response is not JSON")
            return None
    else:
        print(f"Upload failed with status {response.status_code}")
        return None

def check_database_state():
    """Check the current database state"""
    print("\n=== Checking Database State ===")
    
    # Check users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"  User: {user.username} (ID: {user.id})")
    
    # Check resumes
    resumes = Resume.objects.all()
    print(f"Total resumes: {resumes.count()}")
    for resume in resumes:
        print(f"  Resume: {resume.id} - User: {resume.user.username if resume.user else 'None'}")
        print(f"    File: {resume.file}")
        print(f"    Status: {resume.status}")
        print(f"    Created: {resume.created_at}")
        print(f"    Confidence Score: {resume.confidence_score}")
        print("    ---")

def test_resume_list(token):
    """Test getting user's resumes"""
    print("\n=== Testing Resume List API ===")
    
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    response = requests.get('http://localhost:8001/api/resume/list/', headers=headers)
    print(f"List response status: {response.status_code}")
    print(f"List response: {response.text}")

def check_background_processing():
    """Check if background processing is working"""
    print("\n=== Checking Background Processing ===")
    
    # Look for resumes with status 'processing' or 'pending'
    processing_resumes = Resume.objects.filter(status__in=['processing', 'pending'])
    print(f"Resumes being processed: {processing_resumes.count()}")
    
    for resume in processing_resumes:
        print(f"  Resume {resume.id}: Status {resume.status}, Created: {resume.created_at}")
    
    # Check for failed resumes
    failed_resumes = Resume.objects.filter(status='failed')
    print(f"Failed resumes: {failed_resumes.count()}")
    
    for resume in failed_resumes:
        print(f"  Failed Resume {resume.id}: {resume.analysis_result}")

def main():
    print("Starting Comprehensive Resume Upload Test")
    print("==========================================")
    
    # Test user creation and login
    token = test_user_creation_and_login()
    if not token:
        print("Failed to get authentication token. Stopping test.")
        return
    
    # Check initial database state
    check_database_state()
    
    # Test resume upload
    upload_result = test_resume_upload(token)
    
    # Wait a moment for processing
    print("\nWaiting 5 seconds for background processing...")
    time.sleep(5)
    
    # Check database state after upload
    check_database_state()
    
    # Check background processing
    check_background_processing()
    
    # Test resume list
    test_resume_list(token)
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    main()
