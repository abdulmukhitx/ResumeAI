#!/usr/bin/env python3
"""
Test upload functionality and debug 500 error
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from resumes.models import Resume

def test_upload_api():
    """Test the upload API directly"""
    
    # Create a test user if doesn't exist
    test_email = 'testuser@example.com'
    test_user, created = User.objects.get_or_create(
        email=test_email,
        defaults={
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"✓ Created test user: {test_user.email}")
    else:
        print(f"✓ Using existing test user: {test_user.email}")
    
    # First login to get JWT token
    print("\n🔐 Getting JWT token...")
    login_response = requests.post('http://localhost:8000/api/auth/login/', json={
        'email': test_email,
        'password': 'testpass123'
    })
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        access_token = tokens.get('access')
        print(f"✓ Login successful, got access token")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    # Create a test PDF file
    test_pdf_content = b"""%PDF-1.4
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
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000053 00000 n
0000000100 00000 n
0000000176 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
270
%%EOF"""
    
    test_pdf_path = project_root / "test_resume.pdf"
    with open(test_pdf_path, 'wb') as f:
        f.write(test_pdf_content)
    
    print(f"✓ Created test PDF: {test_pdf_path}")
    
    # Test upload
    print("\n📤 Testing resume upload...")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    with open(test_pdf_path, 'rb') as f:
        files = {'file': ('test_resume.pdf', f, 'application/pdf')}
        
        upload_response = requests.post(
            'http://localhost:8000/api/resume/upload/',  # Fixed: singular 'resume'
            headers=headers,
            files=files
        )
    
    print(f"Upload status code: {upload_response.status_code}")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 201:
        print("✅ Upload successful!")
        response_data = upload_response.json()
        resume_id = response_data['resume']['id']
        
        # Check if analysis completes
        print(f"\n🔍 Checking analysis status for resume {resume_id}...")
        import time
        for i in range(10):  # Wait up to 10 seconds
            resume = Resume.objects.get(id=resume_id)
            print(f"Status: {resume.status}")
            if resume.status in ['completed', 'failed']:
                break
            time.sleep(1)
        
        print(f"Final status: {resume.status}")
        if resume.analysis_summary:
            print(f"Analysis summary: {resume.analysis_summary[:200]}...")
    else:
        print("❌ Upload failed!")
    
    # Cleanup
    if test_pdf_path.exists():
        test_pdf_path.unlink()
        print(f"✓ Cleaned up test file")

if __name__ == "__main__":
    test_upload_api()
