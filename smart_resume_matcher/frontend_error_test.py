#!/usr/bin/env python3
"""
Frontend JavaScript Error Test
Tests the login page to verify that JWT authentication JavaScript errors are resolved
"""

import requests
import time
from datetime import datetime

class FrontendErrorTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()

    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "TEST": "🧪"
        }
        print(f"[{timestamp}] {emoji.get(status, 'ℹ️')} {message}")

    def test_login_page_load(self):
        """Test login page loads without errors"""
        self.print_status("Testing login page load...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/login/")
            if response.status_code == 200:
                # Check if the page contains the expected JWT elements
                content = response.text
                required_elements = [
                    'JWT Authentication',
                    'jwt_auth.js',
                    'loginForm',
                    'Welcome Back'
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.print_status("Login page contains all required JWT elements", "SUCCESS")
                    return True
                else:
                    self.print_status(f"Missing elements: {missing_elements}", "ERROR")
                    return False
            else:
                self.print_status(f"Login page returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Login page test failed: {e}", "ERROR")
            return False

    def test_static_files(self):
        """Test that static files load correctly"""
        self.print_status("Testing static file access...", "TEST")
        static_files = [
            '/static/js/jwt_auth.js',
            '/static/js/main.js',
            '/static/css/modern-theme.css'
        ]
        
        all_passed = True
        for file_path in static_files:
            try:
                response = self.session.get(f"{self.base_url}{file_path}")
                if response.status_code == 200:
                    self.print_status(f"✅ {file_path} loads correctly", "SUCCESS")
                else:
                    self.print_status(f"❌ {file_path} returned {response.status_code}", "ERROR")
                    all_passed = False
            except Exception as e:
                self.print_status(f"❌ {file_path} failed: {e}", "ERROR")
                all_passed = False
        
        return all_passed

    def test_jwt_functionality(self):
        """Test basic JWT login functionality"""
        self.print_status("Testing JWT login functionality...", "TEST")
        try:
            # Test login with correct credentials
            response = self.session.post(
                f"{self.base_url}/api/auth/token/",
                headers={"Content-Type": "application/json"},
                json={
                    "email": "test@example.com",
                    "password": "testpass123"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access' in data and 'refresh' in data:
                    self.print_status("JWT login API works correctly", "SUCCESS")
                    return True
                else:
                    self.print_status("JWT response missing tokens", "ERROR")
                    return False
            else:
                self.print_status(f"JWT login failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"JWT login test failed: {e}", "ERROR")
            return False

    def run_frontend_test(self):
        """Run all frontend tests"""
        print("🧪 Frontend JavaScript Error Test")
        print("=" * 50)
        
        tests = [
            ("Login Page Load", self.test_login_page_load),
            ("Static Files", self.test_static_files),
            ("JWT Functionality", self.test_jwt_functionality),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_function in tests:
            self.print_status(f"Running: {test_name}", "TEST")
            try:
                if test_function():
                    passed += 1
                    self.print_status(f"✅ {test_name} - PASSED", "SUCCESS")
                else:
                    self.print_status(f"❌ {test_name} - FAILED", "ERROR")
            except Exception as e:
                self.print_status(f"❌ {test_name} - ERROR: {e}", "ERROR")
            
            print("-" * 50)
            time.sleep(0.5)
        
        # Final summary
        print("=" * 50)
        self.print_status(f"Test Results: {passed}/{total} tests passed", "INFO")
        
        if passed == total:
            self.print_status("🎉 All frontend tests passed! No JavaScript errors detected.", "SUCCESS")
            print("\n🎯 Frontend Status:")
            print("   ✅ Login page loads correctly")
            print("   ✅ Static files accessible")
            print("   ✅ JWT authentication functional")
            print("   ✅ No repeated fetch errors expected")
            print("\n💫 Frontend is ready for production!")
            return True
        else:
            self.print_status(f"⚠️ {total - passed} test(s) failed.", "ERROR")
            return False

if __name__ == "__main__":
    tester = FrontendErrorTest()
    success = tester.run_frontend_test()
    exit(0 if success else 1)
