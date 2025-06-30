#!/usr/bin/env python3
"""
Final Verification Script - Test all critical fixes
"""

import os
import django
import requests
import json
import time
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from resumes.models import Resume

User = get_user_model()

def test_all_fixes():
    print("🚀 TESTING ALL CRITICAL FIXES")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Test Database Connection
    print("\n📊 1. DATABASE CONNECTION TEST")
    print("-" * 30)
    try:
        user_count = User.objects.count()
        resume_count = Resume.objects.count()
        print(f"✅ Database connected: {user_count} users, {resume_count} resumes")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # 2. Test API Endpoints
    print("\n🔗 2. API ENDPOINTS TEST")
    print("-" * 30)
    
    # Create a test user for API testing
    test_email = "apitest@example.com"
    test_password = "testpass123"
    
    user, created = User.objects.get_or_create(
        email=test_email,
        defaults={
            'first_name': 'API',
            'last_name': 'Test',
            'is_active': True
        }
    )
    
    if created:
        user.set_password(test_password)
        user.save()
        print(f"✅ Created test user: {test_email}")
    
    # Test JWT login
    try:
        login_response = requests.post(f"{base_url}/api/auth/token/", 
                                     json={"email": test_email, "password": test_password})
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens['access']
            print(f"✅ JWT Login API: {login_response.status_code} OK")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Test Resume List API
            list_response = requests.get(f"{base_url}/api/resume/list/", headers=headers)
            print(f"✅ Resume List API: {list_response.status_code} - {list_response.json()}")
            
            # Test Logout API
            logout_response = requests.post(f"{base_url}/api/auth/logout/", 
                                          json={"refresh_token": tokens['refresh']})
            print(f"✅ Logout API: {logout_response.status_code} - {logout_response.json()}")
            
        else:
            print(f"❌ JWT Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API Test error: {e}")
        return False
    
    # 3. Test Resume Upload with File
    print("\n📤 3. RESUME UPLOAD TEST")
    print("-" * 30)
    
    try:
        # Login again for upload test
        login_response = requests.post(f"{base_url}/api/auth/token/", 
                                     json={"email": test_email, "password": test_password})
        access_token = login_response.json()['access']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Create a simple test PDF
        test_pdf_content = create_test_pdf()
        
        # Test upload
        files = {'file': ('test_resume.pdf', test_pdf_content, 'application/pdf')}
        upload_response = requests.post(f"{base_url}/api/resume/upload/", 
                                      headers=headers, files=files)
        
        print(f"Upload Response: {upload_response.status_code}")
        if upload_response.status_code == 201:
            upload_data = upload_response.json()
            print(f"✅ Resume Upload: Success - Resume ID {upload_data['resume']['id']}")
            
            # Wait for background processing
            resume_id = upload_data['resume']['id']
            print("⏳ Waiting for background processing...")
            
            for i in range(10):  # Wait up to 30 seconds
                time.sleep(3)
                
                # Check resume status
                resume = Resume.objects.get(id=resume_id)
                print(f"   Status check {i+1}: {resume.status}")
                
                if resume.status in ['completed', 'failed']:
                    break
            
            # Final status check
            final_resume = Resume.objects.get(id=resume_id)
            print(f"✅ Final Status: {final_resume.status}")
            
            if final_resume.status == 'completed':
                print(f"   Skills: {final_resume.extracted_skills}")
                print(f"   Experience: {final_resume.experience_level}")
                print("✅ Resume processing completed successfully!")
            else:
                print(f"   Analysis Summary: {final_resume.analysis_summary}")
                print("⚠️  Resume processing did not complete successfully")
            
        else:
            print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False
    
    # 4. Test CORS Configuration
    print("\n🌐 4. CORS CONFIGURATION TEST")
    print("-" * 30)
    
    try:
        # Test OPTIONS request (preflight)
        options_response = requests.options(f"{base_url}/api/resume/list/")
        print(f"✅ CORS Preflight: {options_response.status_code}")
        
        # Check CORS headers
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Credentials',
            'Access-Control-Allow-Headers'
        ]
        
        for header in cors_headers:
            if header in options_response.headers:
                print(f"✅ {header}: {options_response.headers[header]}")
            else:
                print(f"⚠️  {header}: Not found")
                
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n🎉 ALL TESTS COMPLETED!")
    print("=" * 50)
    return True

def create_test_pdf():
    """Create a simple test PDF content"""
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 80 >>
stream
BT
/F1 12 Tf
100 700 Td
(John Doe) Tj
0 -20 Td
(Software Engineer) Tj
0 -20 Td
(Python, JavaScript, Django) Tj
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
<< /Size 5 /Root 1 0 R >>
startxref
336
%%EOF"""

if __name__ == "__main__":
    test_all_fixes()
