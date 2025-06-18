#!/usr/bin/env python3
"""
Direct server test to isolate the infinite redirect issue
"""

import os
import sys
import django
import requests
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_server_redirect_behavior():
    """Test server behavior without any browser interference"""
    print("🔍 TESTING SERVER REDIRECT BEHAVIOR (No Browser)")
    print("=" * 55)
    
    # Start fresh server test
    base_url = 'http://127.0.0.1:8000'
    
    print("\n1. Testing single redirect behavior...")
    
    try:
        # Test with explicit no-follow redirects
        response = requests.get(f'{base_url}/jobs/ai-matches/', 
                              allow_redirects=False,  # Critical: don't follow redirects
                              timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✓ Server returns single 302 redirect to: {location}")
            
            if '/login/' in location and 'next=' in location:
                print("✓ Redirect is properly formed")
                return True
            else:
                print(f"✗ Unexpected redirect location: {location}")
                return False
        else:
            print(f"✗ Expected 302, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing redirect: {e}")
        return False

def test_login_redirect_chain():
    """Test the full redirect chain manually"""
    print("\n2. Testing login redirect chain...")
    
    session = requests.Session()
    
    try:
        # Step 1: Try to access protected resource
        response1 = session.get('http://127.0.0.1:8000/jobs/ai-matches/', 
                               allow_redirects=False, timeout=5)
        print(f"Step 1 - Jobs page: {response1.status_code}")
        
        if response1.status_code != 302:
            print(f"✗ Expected 302, got {response1.status_code}")
            return False
            
        redirect_url = response1.headers.get('Location', '')
        print(f"Step 1 - Redirect to: {redirect_url}")
        
        # Step 2: Follow redirect to login page
        if redirect_url.startswith('/'):
            redirect_url = 'http://127.0.0.1:8000' + redirect_url
            
        response2 = session.get(redirect_url, allow_redirects=False, timeout=5)
        print(f"Step 2 - Login page: {response2.status_code}")
        
        if response2.status_code == 200:
            print("✓ Login page loads successfully")
            print("✓ No infinite redirect detected in manual test")
            return True
        else:
            print(f"✗ Login page returned {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error in redirect chain test: {e}")
        return False

def main():
    print("🧪 ISOLATED SERVER REDIRECT TEST")
    print("Time:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("Testing server behavior without browser automation")
    print("=" * 60)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test basic server health
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            print("✓ Server is responding")
        else:
            print("✗ Server not responding properly")
            return False
    except Exception as e:
        print(f"✗ Server not accessible: {e}")
        print("Please start Django server: python manage.py runserver 8000")
        return False
    
    # Run isolated tests
    test1 = test_server_redirect_behavior()
    test2 = test_login_redirect_chain()
    
    print("\n" + "=" * 60)
    print("📊 ISOLATED TEST RESULTS:")
    print(f"  🔄 Single Redirect Test: {'PASSED' if test1 else 'FAILED'}")
    print(f"  🔗 Redirect Chain Test: {'PASSED' if test2 else 'FAILED'}")
    
    if test1 and test2:
        print("\n✅ SERVER-SIDE REDIRECT BEHAVIOR IS CORRECT")
        print("The infinite redirect issue is likely CLIENT-SIDE (JavaScript/Browser)")
        print("\n🔍 NEXT STEPS:")
        print("  1. Check for JavaScript that auto-redirects")
        print("  2. Check for browser-based authentication loops")
        print("  3. Test with JavaScript disabled")
        return True
    else:
        print("\n❌ SERVER-SIDE REDIRECT ISSUE DETECTED")
        print("The problem is in the Django backend configuration")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
