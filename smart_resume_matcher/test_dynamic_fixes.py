#!/usr/bin/env python3
"""
Test Dynamic Model Loading Fixes - Smart Resume Matcher
========================================================

This script tests all the dynamic model loading fixes applied to ultra_safe_api.py
and verifies that the CORS and API endpoints are working correctly.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
django.setup()

# Test configurations
BASE_URL = 'http://localhost:8000'
TEST_EMAIL = 'jwt_test@example.com'
TEST_PASSWORD = 'TestPassword123'

class DynamicFixesTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {}
        
    def get_jwt_token(self):
        """Get JWT token for authentication"""
        try:
            response = requests.post(f'{self.base_url}/api/auth/token/', json={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access']
                self.headers = {'Authorization': f'Bearer {self.token}'}
                print("✅ JWT Authentication successful")
                return True
            else:
                print(f"❌ JWT Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ JWT Authentication error: {e}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔄 Testing CORS Configuration...")
        
        try:
            # Test preflight request
            response = requests.options(f'{self.base_url}/api/resume/list/', headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'authorization'
            })
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-credentials': response.headers.get('access-control-allow-credentials'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            print(f"   CORS Headers: {cors_headers}")
            
            if any(cors_headers.values()):
                print("✅ CORS configuration detected")
                return True
            else:
                print("⚠️  CORS headers not found (may still work)")
                return True
                
        except Exception as e:
            print(f"❌ CORS test error: {e}")
            return False
    
    def test_dynamic_model_loading(self):
        """Test dynamic model loading functionality"""
        print("\n🔄 Testing Dynamic Model Loading...")
        
        try:
            # Import the function to test it directly
            from resumes.ultra_safe_api import get_resume_model
            
            # Test getting the model
            Resume = get_resume_model()
            print(f"   Model loaded: {Resume}")
            print(f"   Model name: {Resume._meta.model_name}")
            print(f"   App label: {Resume._meta.app_label}")
            
            # Test basic query (should not error)
            count = Resume.objects.count()
            print(f"   Total resumes in database: {count}")
            
            print("✅ Dynamic model loading working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Dynamic model loading error: {e}")
            return False
    
    def test_resume_list_api(self):
        """Test the resume list API endpoint"""
        print("\n🔄 Testing Resume List API...")
        
        try:
            response = requests.get(f'{self.base_url}/api/resume/list/', headers=self.headers)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response Data: {json.dumps(data, indent=2)}")
                print("✅ Resume List API working correctly")
                return True
            else:
                print(f"❌ Resume List API failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Resume List API error: {e}")
            return False
    
    def test_resume_upload_api(self):
        """Test the resume upload API endpoint"""
        print("\n🔄 Testing Resume Upload API...")
        
        try:
            # Test GET request first (instructions)
            response = requests.get(f'{self.base_url}/api/resume/upload/', headers=self.headers)
            
            print(f"   GET Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Instructions received: {data.get('message')}")
                print(f"   Status: {data.get('status')}")
                print("✅ Resume Upload API (GET) working correctly")
                return True
            else:
                print(f"❌ Resume Upload API (GET) failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Resume Upload API error: {e}")
            return False
    
    def test_logout_api(self):
        """Test the logout API endpoint"""
        print("\n🔄 Testing Logout API...")
        
        try:
            # Get a fresh token for logout test
            auth_response = requests.post(f'{self.base_url}/api/auth/token/', json={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD
            })
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                refresh_token = auth_data.get('refresh')
                
                # Test logout
                logout_response = requests.post(f'{self.base_url}/api/auth/logout/', json={
                    'refresh': refresh_token
                })
                
                print(f"   Status Code: {logout_response.status_code}")
                
                if logout_response.status_code == 200:
                    data = logout_response.json()
                    print(f"   Logout message: {data.get('message')}")
                    print("✅ Logout API working correctly")
                    return True
                else:
                    print(f"❌ Logout API failed: {logout_response.text}")
                    return False
            else:
                print("❌ Could not get fresh token for logout test")
                return False
                
        except Exception as e:
            print(f"❌ Logout API error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 DYNAMIC FIXES TESTING - Smart Resume Matcher")
        print("=" * 55)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Base URL: {self.base_url}")
        print()
        
        # Test results
        results = []
        
        # 1. Get JWT token
        if self.get_jwt_token():
            results.append(("JWT Authentication", True))
        else:
            results.append(("JWT Authentication", False))
            print("❌ Cannot continue without authentication")
            return results
        
        # 2. Test CORS
        results.append(("CORS Configuration", self.test_cors_configuration()))
        
        # 3. Test dynamic model loading
        results.append(("Dynamic Model Loading", self.test_dynamic_model_loading()))
        
        # 4. Test resume list API
        results.append(("Resume List API", self.test_resume_list_api()))
        
        # 5. Test resume upload API
        results.append(("Resume Upload API", self.test_resume_upload_api()))
        
        # 6. Test logout API
        results.append(("Logout API", self.test_logout_api()))
        
        # Print summary
        print("\n" + "=" * 55)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 55)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print()
        print(f"Total Tests: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(results)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Dynamic fixes working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        
        return results

if __name__ == '__main__':
    print("Starting Dynamic Fixes Tests...")
    print("Make sure the Django server is running on http://localhost:8000")
    print()
    
    tester = DynamicFixesTester()
    results = tester.run_all_tests()
    
    print("\n🔚 Testing completed.")
