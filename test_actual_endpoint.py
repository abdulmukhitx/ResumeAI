#!/usr/bin/env python3
"""
Test script to verify which endpoint is actually being called
and test the V4 integration with real API call
"""

import requests
import json
import os
import sys

# Add the Django project directory to Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

def test_actual_endpoint():
    """Test the actual endpoint being used by the frontend"""
    
    print("Testing actual endpoints...")
    
    # Test login first
    login_url = "http://localhost:8000/api/auth/login/"
    login_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        # First try to login to get JWT token
        print("1. Testing login...")
        response = requests.post(login_url, json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access')
            print(f"Got JWT token: {token[:50]}...")
            
            # Test the upload endpoint
            upload_url = "http://localhost:8000/api/resume/upload/"
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # Create a test PDF file
            test_pdf_path = '/home/abdulmukhit/Desktop/ResumeAI/test_file.pdf'
            if not os.path.exists(test_pdf_path):
                print("Creating test PDF file...")
                # Create a simple PDF with ASCII-only content
                test_content = b"""
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
/F1 12 Tf
72 720 Td
(John Doe - Software Engineer) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000201 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
294
%%EOF
"""
                with open(test_pdf_path, 'wb') as f:
                    f.write(test_content)
            
            print("2. Testing resume upload endpoint...")
            with open(test_pdf_path, 'rb') as f:
                files = {'file': ('test_resume.pdf', f, 'application/pdf')}
                
                response = requests.post(upload_url, files=files, headers=headers)
                print(f"Upload response: {response.status_code}")
                print(f"Upload response data: {response.text[:500]}")
                
                if response.status_code == 201:
                    print("✅ Upload successful!")
                    result = response.json()
                    resume_id = result.get('resume', {}).get('id')
                    print(f"Resume ID: {resume_id}")
                    
                    # Check processing status
                    import time
                    for i in range(10):
                        print(f"3. Checking processing status (attempt {i+1})...")
                        time.sleep(2)
                        # You would implement a status check endpoint here
                        break
                else:
                    print(f"❌ Upload failed: {response.text}")
        
        else:
            print(f"❌ Login failed: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def check_server_logs():
    """Check Django server logs for UTF-8 errors"""
    
    log_file = '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/server.log'
    
    if os.path.exists(log_file):
        print("\nChecking server logs for UTF-8 errors...")
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        utf8_errors = []
        for i, line in enumerate(lines[-100:], start=len(lines)-99):  # Check last 100 lines
            if 'utf-8' in line.lower() or 'unicode' in line.lower() or 'encoding' in line.lower():
                utf8_errors.append(f"Line {i}: {line.strip()}")
        
        if utf8_errors:
            print("Found UTF-8 related errors:")
            for error in utf8_errors[-5:]:  # Show last 5 errors
                print(f"  {error}")
        else:
            print("No UTF-8 errors found in recent logs")
    else:
        print("No server log file found")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING ACTUAL ENDPOINT INTEGRATION")
    print("=" * 60)
    
    test_actual_endpoint()
    check_server_logs()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
