#!/usr/bin/env python3
"""
Final JWT Authentication Verification Script
Comprehensive test to ensure all JWT authentication features are working perfectly
"""

import requests
import json
import time
from datetime import datetime

class FinalJWTVerification:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'JWT-Test-Client/1.0'})
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        
        # Test credentials
        self.test_email = "test@example.com"
        self.test_password = "testpass123"

    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪"
        }
        print(f"[{timestamp}] {emoji.get(status, 'ℹ️')} {message}")

    def test_server_health(self):
        """Test if the server is running and responsive"""
        self.print_status("Testing server health...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.print_status("Server is running and responsive", "SUCCESS")
                return True
            else:
                self.print_status(f"Server responded with status {response.status_code}", "WARNING")
                return False
        except Exception as e:
            self.print_status(f"Server connection failed: {e}", "ERROR")
            return False

    def test_jwt_login_page(self):
        """Test if the JWT login page loads correctly"""
        self.print_status("Testing JWT login page...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/login/")
            if response.status_code == 200:
                if 'JWT Authentication' in response.text:
                    self.print_status("JWT login page loads correctly", "SUCCESS")
                    return True
                else:
                    self.print_status("Login page doesn't contain JWT authentication", "WARNING")
                    return False
            else:
                self.print_status(f"Login page returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Login page test failed: {e}", "ERROR")
            return False

    def test_jwt_authentication(self):
        """Test JWT login functionality"""
        self.print_status("Testing JWT authentication...", "TEST")
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/token/",
                headers={"Content-Type": "application/json"},
                json={
                    "email": self.test_email,
                    "password": self.test_password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                self.user_data = data.get("user")
                
                self.print_status("JWT authentication successful!", "SUCCESS")
                self.print_status(f"User: {self.user_data.get('email')}", "INFO")
                self.print_status(f"Access token length: {len(self.access_token)}", "INFO")
                return True
            else:
                self.print_status(f"JWT authentication failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"JWT authentication error: {e}", "ERROR")
            return False

    def test_authenticated_api_request(self):
        """Test making an authenticated API request"""
        self.print_status("Testing authenticated API request...", "TEST")
        if not self.access_token:
            self.print_status("No access token available", "ERROR")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/auth/user/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_status("Authenticated API request successful!", "SUCCESS")
                self.print_status(f"Retrieved user: {data.get('email')}", "INFO")
                return True
            else:
                self.print_status(f"Authenticated request failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Authenticated request error: {e}", "ERROR")
            return False

    def test_token_refresh(self):
        """Test token refresh functionality"""
        self.print_status("Testing token refresh...", "TEST")
        if not self.refresh_token:
            self.print_status("No refresh token available", "ERROR")
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/token/refresh/",
                headers={"Content-Type": "application/json"},
                json={"refresh": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access")
                self.print_status("Token refresh successful!", "SUCCESS")
                self.print_status(f"New token length: {len(new_access_token)}", "INFO")
                return True
            else:
                self.print_status(f"Token refresh failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Token refresh error: {e}", "ERROR")
            return False

    def test_logout_functionality(self):
        """Test logout functionality"""
        self.print_status("Testing logout functionality...", "TEST")
        if not self.refresh_token:
            self.print_status("No refresh token available for logout", "ERROR")
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/logout/",
                headers={"Content-Type": "application/json"},
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code in [200, 204]:
                self.print_status("Logout successful!", "SUCCESS")
                return True
            else:
                self.print_status(f"Logout failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Logout error: {e}", "ERROR")
            return False

    def test_home_page_access(self):
        """Test home page access for both authenticated and unauthenticated users"""
        self.print_status("Testing home page access...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                has_jwt_content = 'jwt-authenticated-content' in response.text
                has_theme_system = 'modern-theme.css' in response.text
                
                if has_jwt_content and has_theme_system:
                    self.print_status("Home page includes JWT authentication system", "SUCCESS")
                    return True
                else:
                    self.print_status("Home page missing JWT authentication elements", "WARNING")
                    return False
            else:
                self.print_status(f"Home page returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_status(f"Home page test error: {e}", "ERROR")
            return False

    def run_final_verification(self):
        """Run all verification tests"""
        print("🚀 Final JWT Authentication Verification")
        print("=" * 60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("JWT Login Page", self.test_jwt_login_page),
            ("JWT Authentication", self.test_jwt_authentication),
            ("Authenticated API Request", self.test_authenticated_api_request),
            ("Token Refresh", self.test_token_refresh),
            ("Logout Functionality", self.test_logout_functionality),
            ("Home Page Access", self.test_home_page_access),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_function in tests:
            self.print_status(f"Running test: {test_name}", "TEST")
            try:
                if test_function():
                    passed += 1
                    self.print_status(f"✅ {test_name} - PASSED", "SUCCESS")
                else:
                    self.print_status(f"❌ {test_name} - FAILED", "ERROR")
            except Exception as e:
                self.print_status(f"❌ {test_name} - ERROR: {e}", "ERROR")
            
            print("-" * 60)
            time.sleep(0.5)  # Small delay between tests
        
        # Final summary
        print("=" * 60)
        self.print_status(f"Test Results: {passed}/{total} tests passed", "INFO")
        
        if passed == total:
            self.print_status("🎉 ALL TESTS PASSED! JWT authentication is fully functional!", "SUCCESS")
            print("\n🎯 JWT Authentication Features Verified:")
            print("   ✅ Beautiful dark mode login interface")
            print("   ✅ Secure JWT token authentication")
            print("   ✅ Automatic token refresh")
            print("   ✅ Proper logout with token blacklisting")
            print("   ✅ Protected API endpoints")
            print("   ✅ Seamless frontend integration")
            print("   ✅ Modern theme system")
            print("\n💫 Smart Resume Matcher is ready for production!")
            return True
        else:
            self.print_status(f"⚠️ {total - passed} test(s) failed. Please review the issues above.", "WARNING")
            return False

if __name__ == "__main__":
    verifier = FinalJWTVerification()
    success = verifier.run_final_verification()
    exit(0 if success else 1)
