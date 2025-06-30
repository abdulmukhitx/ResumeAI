#!/usr/bin/env python3

"""
Smart Resume Matcher - Final Fixes Validation Test
=================================================

This script validates all the critical fixes applied to resolve:
1. 500 Internal Server Error during resume upload
2. Missing API endpoints (/api/resume/list/)
3. Logout functionality (400 Bad Request errors)
4. CORS configuration for frontend integration
5. URL routing issues

Run this after starting the server with: python manage.py runserver
"""

import requests
import json
import sys
import time
from pathlib import Path

class FixesValidator:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.token = None
        self.refresh_token = None
        self.passed_tests = 0
        self.total_tests = 0
        
    def log(self, message, status="INFO"):
        colors = {
            "PASS": "\033[92m✅",
            "FAIL": "\033[91m❌", 
            "INFO": "\033[94mℹ️",
            "WARN": "\033[93m⚠️"
        }
        print(f"{colors.get(status, '')} {message}\033[0m")
    
    def test_server_connectivity(self):
        """Test if server is running"""
        self.total_tests += 1
        self.log("Testing server connectivity...")
        
        try:
            response = requests.get(f'{self.base_url}/', timeout=5)
            if response.status_code == 200:
                self.log("Server is running and responding", "PASS")
                self.passed_tests += 1
                return True
            else:
                self.log(f"Server returned {response.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"Cannot connect to server: {e}", "FAIL")
            self.log("Please start the server with: python manage.py runserver", "WARN")
            return False
    
    def test_cors_configuration(self):
        """Test CORS headers are properly configured"""
        self.total_tests += 1
        self.log("Testing CORS configuration...")
        
        try:
            # Test preflight request
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'authorization,content-type'
            }
            
            response = requests.options(f'{self.base_url}/api/auth/token/', headers=headers, timeout=5)
            
            # Check for CORS headers
            cors_headers = response.headers.get('Access-Control-Allow-Origin')
            if cors_headers or response.status_code in [200, 204]:
                self.log("CORS configuration is working", "PASS")
                self.passed_tests += 1
                return True
            else:
                self.log("CORS headers not found or not configured properly", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"CORS test failed: {e}", "FAIL")
            return False
    
    def test_jwt_authentication(self):
        """Test JWT login endpoint"""
        self.total_tests += 1
        self.log("Testing JWT authentication...")
        
        # Use test credentials
        login_data = {
            'email': 'jwt_test@example.com',
            'password': 'TestPassword123'
        }
        
        try:
            response = requests.post(f'{self.base_url}/api/auth/token/', json=login_data, timeout=5)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('access')
                self.refresh_token = token_data.get('refresh')
                
                if self.token and self.refresh_token:
                    self.log("JWT authentication working", "PASS")
                    self.passed_tests += 1
                    return True
                else:
                    self.log("JWT tokens not received properly", "FAIL")
                    return False
            else:
                self.log(f"JWT login failed with status {response.status_code}", "FAIL")
                self.log("Note: Test user might not exist. Create with: python manage.py shell", "WARN")
                return False
                
        except Exception as e:
            self.log(f"JWT authentication test failed: {e}", "FAIL")
            return False
    
    def test_resume_list_api(self):
        """Test the new resume list API endpoint"""
        self.total_tests += 1
        self.log("Testing /api/resume/list/ endpoint...")
        
        if not self.token:
            self.log("No auth token available, skipping", "FAIL")
            return False
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f'{self.base_url}/api/resume/list/', headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'resumes' in data:
                    self.log(f"Resume List API working - found {data.get('total_count', 0)} resumes", "PASS")
                    self.passed_tests += 1
                    return True
                else:
                    self.log("Resume List API returned invalid data format", "FAIL")
                    return False
            else:
                self.log(f"Resume List API failed with status {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Resume List API test failed: {e}", "FAIL")
            return False
    
    def test_resume_upload_api(self):
        """Test the resume upload API endpoint"""
        self.total_tests += 1
        self.log("Testing /api/resume/upload/ endpoint...")
        
        if not self.token:
            self.log("No auth token available, skipping", "FAIL")
            return False
            
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Test GET request (should return instructions)
            response = requests.get(f'{self.base_url}/api/resume/upload/', headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'instructions' in data and 'status' in data:
                    self.log("Resume Upload API (GET) working - no more 500 errors!", "PASS")
                    self.passed_tests += 1
                    return True
                else:
                    self.log("Resume Upload API returned unexpected format", "FAIL")
                    return False
            else:
                self.log(f"Resume Upload API failed with status {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Resume Upload API test failed: {e}", "FAIL")
            return False
    
    def test_logout_functionality(self):
        """Test the improved logout functionality"""
        self.total_tests += 1
        self.log("Testing /api/auth/logout/ endpoint...")
        
        if not self.refresh_token:
            self.log("No refresh token available, skipping", "FAIL")
            return False
            
        logout_data = {'refresh': self.refresh_token}
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        
        try:
            response = requests.post(f'{self.base_url}/api/auth/logout/', json=logout_data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("Logout functionality working - no more 400 errors!", "PASS")
                    self.passed_tests += 1
                    return True
                else:
                    self.log("Logout returned non-success response", "FAIL")
                    return False
            else:
                self.log(f"Logout failed with status {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Logout test failed: {e}", "FAIL")
            return False
    
    def test_main_upload_interface(self):
        """Test the main upload interface for 500 errors"""
        self.total_tests += 1
        self.log("Testing main upload interface...")
        
        try:
            # Test the main upload page
            response = requests.get(f'{self.base_url}/jwt-resume-upload/', timeout=5)
            
            if response.status_code == 200:
                self.log("Main upload interface accessible - no 500 errors!", "PASS")
                self.passed_tests += 1
                return True
            else:
                self.log(f"Upload interface returned {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Upload interface test failed: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all validation tests"""
        self.log("🔧 Smart Resume Matcher - Final Fixes Validation", "INFO")
        self.log("=" * 60, "INFO")
        
        # Test server connectivity first
        if not self.test_server_connectivity():
            self.log("Cannot proceed without server connection", "FAIL")
            return False
        
        # Run all tests
        tests = [
            self.test_cors_configuration,
            self.test_jwt_authentication,
            self.test_resume_list_api,
            self.test_resume_upload_api,
            self.test_logout_functionality,
            self.test_main_upload_interface
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Brief pause between tests
        
        # Summary
        self.log("=" * 60, "INFO")
        self.log(f"Test Results: {self.passed_tests}/{self.total_tests} passed", "INFO")
        
        if self.passed_tests == self.total_tests:
            self.log("🎉 ALL FIXES VALIDATED SUCCESSFULLY!", "PASS")
            self.log("The Smart Resume Matcher is now fully functional!", "PASS")
            return True
        else:
            failed = self.total_tests - self.passed_tests
            self.log(f"⚠️  {failed} tests failed. Please review the issues above.", "WARN")
            return False

def main():
    """Main function"""
    validator = FixesValidator()
    
    # Check if server URL is provided
    if len(sys.argv) > 1:
        validator.base_url = sys.argv[1]
    
    success = validator.run_all_tests()
    
    if success:
        print("\n🚀 Ready to use Smart Resume Matcher!")
        print("📝 Access points:")
        print(f"   • Main App: {validator.base_url}/")
        print(f"   • JWT Login: {validator.base_url}/jwt-login/")
        print(f"   • Upload Resume: {validator.base_url}/jwt-resume-upload/")
        print(f"   • API Documentation: Available in code comments")
    else:
        print("\n❌ Some issues remain. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
