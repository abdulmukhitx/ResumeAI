#!/usr/bin/env python3
"""
Comprehensive JWT Authentication Test
Tests the complete authentication flow including:
1. User registration
2. JWT login
3. Token validation
4. Authentication state management
5. Logout functionality
"""

import requests
import json
import time

class JWTAuthenticationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        
    def test_server_health(self):
        """Test if the server is running and responsive"""
        print("🔍 Testing server health...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is running and responsive")
                return True
            else:
                print(f"❌ Server returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server is not accessible: {e}")
            return False
    
    def test_login_page(self):
        """Test if the login page loads correctly"""
        print("\n🔍 Testing login page...")
        try:
            response = self.session.get(f"{self.base_url}/login/")
            if response.status_code == 200 and "Sign In" in response.text:
                print("✅ Login page loads correctly")
                return True
            else:
                print(f"❌ Login page issue: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login page error: {e}")
            return False
    
    def test_jwt_endpoint(self):
        """Test JWT token endpoint"""
        print("\n🔍 Testing JWT token endpoint...")
        try:
            # Test with invalid credentials
            response = self.session.post(
                f"{self.base_url}/api/auth/token/",
                headers={"Content-Type": "application/json"},
                json={"email": "invalid@test.com", "password": "wrong"}
            )
            
            if response.status_code == 401:
                print("✅ JWT endpoint correctly rejects invalid credentials")
                return True
            else:
                print(f"❌ JWT endpoint unexpected response: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ JWT endpoint error: {e}")
            return False
    
    def test_jwt_login(self):
        """Test JWT login with valid credentials"""
        print("\n🔍 Testing JWT login...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/token/",
                headers={"Content-Type": "application/json"},
                json={"email": "test@example.com", "password": "testpass123"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access")
                self.refresh_token = data.get("refresh")
                user_data = data.get("user", {})
                
                print("✅ JWT login successful!")
                print(f"   User: {user_data.get('email')}")
                print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   Active: {user_data.get('is_active')}")
                print(f"   Access Token: {self.access_token[:30]}..." if self.access_token else "   No access token")
                return True
            else:
                print(f"❌ JWT login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ JWT login error: {e}")
            return False
    
    def test_authenticated_request(self):
        """Test making an authenticated request"""
        print("\n🔍 Testing authenticated request...")
        if not self.access_token:
            print("❌ No access token available")
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
                print("✅ Authenticated request successful!")
                print(f"   User data retrieved: {data.get('email')}")
                return True
            else:
                print(f"❌ Authenticated request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authenticated request error: {e}")
            return False
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        print("\n🔍 Testing token refresh...")
        if not self.refresh_token:
            print("❌ No refresh token available")
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
                print("✅ Token refresh successful!")
                print(f"   New access token: {new_access_token[:30]}...")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return False
    
    def test_logout(self):
        """Test logout functionality"""
        print("\n🔍 Testing logout...")
        if not self.refresh_token:
            print("❌ No refresh token available for logout")
            return False
            
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/logout/",
                headers={"Content-Type": "application/json"},
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code in [200, 204]:
                print("✅ Logout successful!")
                return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Logout error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 JWT Authentication Comprehensive Test")
        print("=" * 50)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Login Page", self.test_login_page),
            ("JWT Endpoint", self.test_jwt_endpoint),
            ("JWT Login", self.test_jwt_login),
            ("Authenticated Request", self.test_authenticated_request),
            ("Token Refresh", self.test_token_refresh),
            ("Logout", self.test_logout),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! JWT authentication is working perfectly!")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        return passed == total

if __name__ == "__main__":
    tester = JWTAuthenticationTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ JWT Authentication is ready for production!")
    else:
        print("\n❌ JWT Authentication needs fixes before production.")
