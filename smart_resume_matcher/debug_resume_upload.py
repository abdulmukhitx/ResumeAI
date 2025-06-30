#!/usr/bin/env python3
"""
Debug script to test resume upload and background processing
"""

import os
import django
import requests
import json
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import Resume
from django.test import Client
from django.contrib.auth import authenticate

User = get_user_model()

def test_resume_upload_debug():
    print("🔍 DEBUGGING RESUME UPLOAD ISSUE")
    print("=" * 50)
    
    # Check current database state
    print(f"📊 Users in database: {User.objects.count()}")
    print(f"📊 Resumes in database: {Resume.objects.count()}")
    
    # Get or create a test user
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    user, created = User.objects.get_or_create(
        email=test_email,
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        user.set_password(test_password)
        user.save()
        print(f"✅ Created test user: {test_email}")
    else:
        print(f"✅ Using existing test user: {test_email}")
    
    # Test JWT token generation
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    print(f"✅ Generated JWT token for user")
    
    # Test API call to get user resume list
    print("\n🧪 TESTING API ENDPOINTS")
    print("-" * 30)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Test resume list endpoint
    try:
        response = requests.get('http://localhost:8000/api/resume/list/', headers=headers)
        print(f"📋 Resume List API: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Resume List API Error: {e}")
    
    # Check if user has any resumes
    user_resumes = Resume.objects.filter(user=user)
    print(f"\n📄 User resumes in database: {user_resumes.count()}")
    
    for resume in user_resumes:
        print(f"  - {resume.original_filename} (Status: {resume.status})")
        print(f"    Skills: {len(resume.extracted_skills or [])}")
        print(f"    Created: {resume.created_at}")
    
    # Create a simple test PDF for upload
    test_pdf_content = b"""
%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 24 Tf
100 700 Td
(Test Resume) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
296
%%EOF
"""
    
    # Save test PDF
    test_pdf_path = Path("test_resume.pdf")
    with open(test_pdf_path, "wb") as f:
        f.write(test_pdf_content)
    
    print(f"\n✅ Created test PDF: {test_pdf_path}")
    
    # Test upload
    try:
        upload_headers = {'Authorization': f'Bearer {access_token}'}
        files = {'file': ('test_resume.pdf', open(test_pdf_path, 'rb'), 'application/pdf')}
        
        response = requests.post('http://localhost:8000/api/resume/upload/', 
                               headers=upload_headers, 
                               files=files)
        
        print(f"\n📤 Upload Response: {response.status_code}")
        print(f"Response data: {response.json()}")
        
        # Check database after upload
        print(f"\n📊 After upload - Resumes in database: {Resume.objects.count()}")
        
        # Wait a bit for background processing
        import time
        print("⏳ Waiting 5 seconds for background processing...")
        time.sleep(5)
        
        # Check again
        user_resumes_after = Resume.objects.filter(user=user)
        print(f"📊 User resumes after processing: {user_resumes_after.count()}")
        
        for resume in user_resumes_after:
            print(f"  - {resume.original_filename}")
            print(f"    Status: {resume.status}")
            print(f"    Skills: {resume.extracted_skills}")
            print(f"    Analysis: {resume.analysis_summary}")
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
    
    finally:
        # Clean up
        if test_pdf_path.exists():
            test_pdf_path.unlink()

if __name__ == "__main__":
    test_resume_upload_debug()
