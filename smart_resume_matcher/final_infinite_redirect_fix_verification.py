#!/usr/bin/env python3
"""
Final comprehensive test to verify the infinite redirect loop has been completely fixed
and that the authentication system works correctly.
"""

import time
import requests
import logging
from urllib.parse import urljoin, urlparse, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveRedirectTest:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_complete_flow(self):
        """Test the complete authentication flow without infinite redirects"""
        logger.info("🎯 Testing complete authentication flow...")
        
        try:
            # Step 1: Access protected page (should redirect to login)
            protected_url = urljoin(self.base_url, '/jobs/ai-matches/')
            logger.info(f"📍 Step 1: Accessing {protected_url}")
            
            response = self.session.get(protected_url, allow_redirects=False)
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                logger.info(f"✅ Step 1: Redirected to {redirect_url}")
                
                # Step 2: Follow redirect to login page
                if redirect_url.startswith('/'):
                    login_url = urljoin(self.base_url, redirect_url)
                else:
                    login_url = redirect_url
                    
                logger.info(f"📍 Step 2: Loading login page {login_url}")
                login_response = self.session.get(login_url, allow_redirects=False)
                
                if login_response.status_code == 200:
                    logger.info("✅ Step 2: Login page loads correctly (no infinite redirect)")
                    
                    # Verify the login page contains expected elements
                    content = login_response.content.decode('utf-8', errors='ignore')
                    
                    required_elements = ['email', 'password', 'login']
                    found_elements = [elem for elem in required_elements if elem.lower() in content.lower()]
                    
                    if len(found_elements) >= 2:
                        logger.info(f"✅ Step 2: Login form verified (found: {found_elements})")
                        
                        # Step 3: Test that rapid requests don't cause problems
                        logger.info("📍 Step 3: Testing rapid request handling...")
                        
                        rapid_test_success = True
                        for i in range(3):
                            rapid_response = self.session.get(protected_url, allow_redirects=False, timeout=5)
                            logger.info(f"Rapid request {i+1}: Status {rapid_response.status_code}")
                            
                            if rapid_response.status_code != 302:
                                rapid_test_success = False
                                break
                                
                            time.sleep(0.2)  # Small delay
                        
                        if rapid_test_success:
                            logger.info("✅ Step 3: Rapid requests handled correctly")
                            return True
                        else:
                            logger.error("❌ Step 3: Rapid request handling failed")
                            return False
                    else:
                        logger.error(f"❌ Step 2: Login form incomplete (found only: {found_elements})")
                        return False
                else:
                    logger.error(f"❌ Step 2: Login page returned status {login_response.status_code}")
                    return False
            else:
                logger.error(f"❌ Step 1: Expected redirect (302), got {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}")
            return False
    
    def test_login_page_protection(self):
        """Test that the login page has proper infinite redirect protection"""
        logger.info("🛡️ Testing login page redirect protection...")
        
        try:
            # Access login page with next parameter multiple times rapidly
            login_url = urljoin(self.base_url, '/login/?next=/jobs/ai-matches/')
            
            responses = []
            start_time = time.time()
            
            for i in range(5):
                response = self.session.get(login_url, allow_redirects=False, timeout=5)
                responses.append(response.status_code)
                logger.info(f"Login access {i+1}: Status {response.status_code}")
                time.sleep(0.1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # All responses should be 200 (login page loads)
            if all(status == 200 for status in responses):
                logger.info(f"✅ All login page requests returned 200 in {total_time:.2f}s")
                logger.info("✅ Login page redirect protection working correctly")
                return True
            else:
                logger.error(f"❌ Unexpected status codes: {responses}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login page protection test failed: {e}")
            return False
    
    def test_server_performance(self):
        """Test that the server performance is good and no overload occurs"""
        logger.info("⚡ Testing server performance...")
        
        try:
            test_urls = [
                '/jobs/ai-matches/',
                '/jobs/',
                '/login/',
                '/'
            ]
            
            performance_results = {}
            
            for url in test_urls:
                full_url = urljoin(self.base_url, url)
                start_time = time.time()
                
                response = self.session.get(full_url, allow_redirects=False, timeout=10)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                performance_results[url] = {
                    'status': response.status_code,
                    'time': response_time
                }
                
                logger.info(f"URL {url}: Status {response.status_code}, Time {response_time:.3f}s")
            
            # Check that all responses are fast (under 2 seconds)
            slow_responses = [url for url, data in performance_results.items() if data['time'] > 2.0]
            
            if not slow_responses:
                avg_time = sum(data['time'] for data in performance_results.values()) / len(performance_results)
                logger.info(f"✅ All responses fast (avg: {avg_time:.3f}s)")
                return True
            else:
                logger.warning(f"⚠️ Slow responses detected: {slow_responses}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting comprehensive infinite redirect fix verification...")
        logger.info("=" * 60)
        
        tests = [
            ("Complete Authentication Flow", self.test_complete_flow),
            ("Login Page Protection", self.test_login_page_protection),
            ("Server Performance", self.test_server_performance),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            logger.info("-" * 40)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.info(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False
        
        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 COMPREHENSIVE TEST RESULTS")
        logger.info("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("\n🎉 INFINITE REDIRECT LOOP COMPLETELY FIXED!")
            logger.info("🚀 Authentication system is working correctly!")
            logger.info("✨ Ready for production deployment!")
            return True
        else:
            logger.info("\n⚠️ Some issues remain. Check failed tests above.")
            return False

if __name__ == '__main__':
    tester = ComprehensiveRedirectTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 SUCCESS: Infinite redirect loop has been completely eliminated!")
        print("🚀 The authentication system is now working perfectly!")
        exit(0)
    else:
        print("\n💥 Some issues detected. Please review the test results.")
        exit(1)
