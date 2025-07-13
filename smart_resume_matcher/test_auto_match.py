#!/usr/bin/env python3
"""
Test Auto-Match Functionality
This script tests the auto-match endpoint to ensure it's working correctly.
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_auto_match_endpoint():
    """Test the auto-match endpoint"""
    print("🧪 Testing Auto-Match Functionality...")
    
    # First, get a valid JWT token
    print("1. Logging in to get JWT token...")
    login_response = requests.post('http://localhost:8000/api/auth/login/', 
                                 json={'email': 'test@example.com', 'password': 'testpass123'})
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token_data = login_response.json()
    access_token = token_data['access']
    print(f"✅ Login successful, got token: {access_token[:20]}...")
    
    # Test auto-match with valid token
    print("\n2. Testing auto-match with valid token...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    response = requests.get('http://localhost:8000/jobs/ai-matches/?auto_match=true', headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Auto-match failed: {response.status_code}")
        print(response.text)
        return False
    
    try:
        data = response.json()
        print(f"✅ Auto-match successful!")
        print(f"   - Success: {data.get('success', False)}")
        print(f"   - Matches found: {len(data.get('matches', []))}")
        print(f"   - Stats: {data.get('stats', {})}")
        
        # Show some sample matches
        matches = data.get('matches', [])
        if matches:
            print(f"\n   Sample matches:")
            for i, match in enumerate(matches[:3]):
                job = match.get('job', {})
                print(f"   {i+1}. {job.get('title', 'N/A')} - {match.get('match_score', 0)}% match")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        print(f"Response text: {response.text}")
        return False
    
    # Test with invalid token
    print("\n3. Testing auto-match with invalid token...")
    invalid_headers = {
        'Authorization': 'Bearer invalid_token',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    response = requests.get('http://localhost:8000/jobs/ai-matches/?auto_match=true', headers=invalid_headers)
    
    if response.status_code == 401:
        try:
            error_data = response.json()
            print(f"✅ Invalid token correctly handled: {error_data.get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print(f"❌ Invalid token response not JSON: {response.text}")
            return False
    else:
        print(f"❌ Expected 401 for invalid token, got {response.status_code}")
        return False
    
    # Test without token
    print("\n4. Testing auto-match without token...")
    no_token_headers = {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    response = requests.get('http://localhost:8000/jobs/ai-matches/?auto_match=true', headers=no_token_headers)
    
    if response.status_code == 401:
        try:
            error_data = response.json()
            print(f"✅ No token correctly handled: {error_data.get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print(f"❌ No token response not JSON: {response.text}")
            return False
    else:
        print(f"❌ Expected 401 for no token, got {response.status_code}")
        return False
    
    print("\n🎉 All auto-match tests passed!")
    return True

if __name__ == '__main__':
    success = test_auto_match_endpoint()
    sys.exit(0 if success else 1)
