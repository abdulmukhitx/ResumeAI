#!/usr/bin/env python3
"""
Test to verify that the infinite redirect loop prevention is working correctly.
This test simulates the conditions that were causing the infinite redirect loop.
"""

import time
import requests
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfiniteRedirectTest:
    def __init__(self, base_url='http://127.0.0.1:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        # Set a reasonable redirect limit instead of 0
        self.session.max_redirects = 3
        
    def test_redirect_prevention(self):
        """Test that the infinite redirect loop has been prevented"""
        logger.info("🧪 Testing infinite redirect prevention...")
        
        # Simulate the problematic scenario:
        # 1. Access /jobs/ai-matches/ without authentication
        # 2. Should redirect to login with next parameter
        # 3. Login page should NOT immediately redirect back
        
        try:
            # Step 1: Try to access protected page
            protected_url = urljoin(self.base_url, '/jobs/ai-matches/')
            logger.info(f"📍 Accessing protected URL: {protected_url}")
            
            response = self.session.get(protected_url, allow_redirects=False)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 302:
                redirect_location = response.headers.get('Location', '')
                logger.info(f"🔄 Server redirect to: {redirect_location}")
                
                # Check if redirected to login with next parameter
                if '/login/' in redirect_location and 'next=' in redirect_location:
                    logger.info("✅ Correct server-side redirect behavior")
                    
                    # Step 2: Access the login page (this should NOT cause immediate redirect)
                    # Handle relative URLs by making them absolute
                    if redirect_location.startswith('/'):
                        login_url = urljoin(self.base_url, redirect_location)
                    else:
                        login_url = redirect_location
                        
                    login_response = self.session.get(login_url, allow_redirects=False)
                    logger.info(f"Login page status: {login_response.status_code}")
                    
                    if login_response.status_code == 200:
                        logger.info("✅ Login page loads correctly without immediate redirect")
                        
                        # Check that the response contains login-related content
                        content = login_response.content.decode('utf-8', errors='ignore')
                        login_indicators = [
                            'login-form',
                            'jwt-login', 
                            'email',
                            'password',
                            'Login',
                            'auth-container',
                            'Sign in'
                        ]
                        
                        found_indicators = [indicator for indicator in login_indicators if indicator in content]
                        
                        if found_indicators:
                            logger.info(f"✅ Login page content verified. Found indicators: {found_indicators}")
                            return True
                        else:
                            logger.warning("⚠️ Login form indicators not found in response")
                            # Log a snippet of the response for debugging
                            logger.warning(f"Response content preview: {content[:500]}...")
                            return False
                    else:
                        logger.error(f"❌ Login page returned unexpected status: {login_response.status_code}")
                        return False
                else:
                    logger.error(f"❌ Unexpected redirect location: {redirect_location}")
                    return False
            else:
                logger.error(f"❌ Expected 302 redirect, got {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}")
            return False
    
    def test_rapid_requests(self):
        """Test that rapid requests don't cause server overload"""
        logger.info("🧪 Testing rapid request handling...")
        
        try:
            # Make several rapid requests to simulate the infinite loop scenario
            protected_url = urljoin(self.base_url, '/jobs/ai-matches/')
            request_count = 5
            start_time = time.time()
            
            for i in range(request_count):
                response = self.session.get(protected_url, allow_redirects=False, timeout=5)
                logger.info(f"Request {i+1}: Status {response.status_code}")
                
                # Small delay to prevent overwhelming the server
                time.sleep(0.1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            logger.info(f"✅ Completed {request_count} requests in {total_time:.2f} seconds")
            logger.info(f"Average response time: {total_time/request_count:.2f} seconds per request")
            
            if total_time < 10:  # Should complete within 10 seconds
                logger.info("✅ Server responds promptly to rapid requests")
                return True
            else:
                logger.warning("⚠️ Server response time seems slow")
                return False
                
        except Exception as e:
            logger.error(f"❌ Rapid request test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all infinite redirect prevention tests"""
        logger.info("🚀 Starting infinite redirect prevention tests...")
        logger.info("=" * 50)
        
        tests = [
            ("Redirect Prevention", self.test_redirect_prevention),
            ("Rapid Request Handling", self.test_rapid_requests),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            logger.info("-" * 30)
            
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
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! Infinite redirect loop has been prevented!")
            return True
        else:
            logger.info("⚠️ Some tests failed. Please check the issues above.")
            return False

if __name__ == '__main__':
    # Test the infinite redirect prevention
    tester = InfiniteRedirectTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 SUCCESS: Infinite redirect loop prevention is working!")
        exit(0)
    else:
        print("\n💥 FAILURE: Issues detected with redirect prevention")
        exit(1)
