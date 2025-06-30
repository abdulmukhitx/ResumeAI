#!/usr/bin/env python3
"""
Simple Upload Test - No Analysis
=================================

Test the upload API without any analysis to isolate the issue.
"""

import requests
import sys

def test_upload_simple():
    """Test upload with analysis disabled"""
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/auth/token/"
    upload_url = f"{base_url}/api/resume/upload/"
    
    # Test credentials
    test_email = "test@example.com"
    test_password = "testpass123"
    
    print("🔍 Testing Upload API (Analysis Disabled)")
    print("=" * 50)
    
    # Step 1: Login
    print("Step 1: Logging in...")
    try:
        login_response = requests.post(login_url, json={
            "email": test_email,
            "password": test_password
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        access_token = login_response.json()['access']
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Create a simple PDF
    print("Step 2: Creating test PDF...")
    pdf_content = b"""%PDF-1.4
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
/Length 50
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume - No Analysis) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000189 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
284
%%EOF"""
    
    # Step 3: Upload
    print("Step 3: Uploading PDF...")
    try:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        files = {
            'file': ('test_simple.pdf', pdf_content, 'application/pdf')
        }
        
        upload_response = requests.post(upload_url, headers=headers, files=files)
        
        print(f"Upload status: {upload_response.status_code}")
        print(f"Response: {upload_response.text}")
        
        if upload_response.status_code == 201:
            print("✅ Upload successful!")
            return True
        else:
            print("❌ Upload failed")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    success = test_upload_simple()
    sys.exit(0 if success else 1)
