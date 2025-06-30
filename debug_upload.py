#!/usr/bin/env python3
"""
Test the resume upload API directly to diagnose the 500 error
"""
import requests
import os

def test_upload_api():
    base_url = "http://127.0.0.1:8000"
    
    # First, get JWT token
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    print("🔐 Getting JWT token...")
    try:
        login_response = requests.post(f"{base_url}/api/auth/token/", json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens['access']
            print("✅ JWT token obtained successfully")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Create a simple test PDF content
    test_pdf_content = b"""%PDF-1.4
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
100 700 Td
(Test Resume Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000209 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
301
%%EOF"""
    
    # Save test PDF
    test_pdf_path = "/tmp/test_resume_debug.pdf"
    with open(test_pdf_path, 'wb') as f:
        f.write(test_pdf_content)
    
    print("📄 Created test PDF")
    
    # Test upload
    print("📤 Testing upload...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': ('test_resume_debug.pdf', f, 'application/pdf')}
            
            upload_response = requests.post(
                f"{base_url}/api/resume/upload/",
                files=files,
                headers=headers
            )
            
        print(f"Upload response status: {upload_response.status_code}")
        print(f"Upload response headers: {dict(upload_response.headers)}")
        print(f"Upload response text: {upload_response.text}")
        
        if upload_response.status_code == 201:
            print("✅ Upload successful!")
            response_data = upload_response.json()
            print(f"Response data: {response_data}")
        else:
            print(f"❌ Upload failed with status {upload_response.status_code}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
    
    # Clean up
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)

if __name__ == "__main__":
    test_upload_api()
