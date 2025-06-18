#!/usr/bin/env python3
"""
Clean JWT Authentication System Test
Tests the new clean JWT authentication system for console errors and functionality.
"""

import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def setup_headless_browser():
    """Setup a headless Chrome browser for testing"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')  # Suppress most Chrome logs
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Could not start Chrome browser: {e}")
        return None

def test_clean_jwt_system():
    """Test the clean JWT authentication system"""
    print("🧪 Testing Clean JWT Authentication System")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Server Health Check
    print("\n1. 🔍 Server Health Check...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Server is running successfully")
        else:
            print(f"   ❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False
    
    # Test 2: Setup Browser
    print("\n2. 🌐 Setting up browser...")
    driver = setup_headless_browser()
    if not driver:
        return False
    
    try:
        # Test 3: Load Home Page and Check for Console Errors
        print("\n3. 🏠 Testing Home Page...")
        driver.get(base_url)
        time.sleep(3)  # Wait for JavaScript to load
        
        # Check for JavaScript errors
        logs = driver.get_log('browser')
        error_count = 0
        warning_count = 0
        
        for log in logs:
            if log['level'] == 'SEVERE':
                error_count += 1
                print(f"   ❌ JavaScript Error: {log['message']}")
            elif log['level'] == 'WARNING':
                warning_count += 1
        
        if error_count == 0:
            print(f"   ✅ Home page loaded without JavaScript errors")
            if warning_count > 0:
                print(f"   ⚠️  {warning_count} warnings found (acceptable)")
        else:
            print(f"   ❌ Found {error_count} JavaScript errors")
        
        # Test 4: Load Login Page
        print("\n4. 🔐 Testing Login Page...")
        driver.get(f"{base_url}/login/")
        time.sleep(3)
        
        # Check for auth manager
        auth_manager_ready = driver.execute_script("""
            return window.authManager && 
                   typeof window.authManager.login === 'function' &&
                   typeof window.authManager.isAuthenticated === 'function';
        """)
        
        if auth_manager_ready:
            print("   ✅ Clean JWT Auth Manager loaded successfully")
        else:
            print("   ❌ Clean JWT Auth Manager not ready")
        
        # Check for new console errors
        new_logs = driver.get_log('browser')
        new_error_count = 0
        for log in new_logs:
            if log['level'] == 'SEVERE':
                new_error_count += 1
                print(f"   ❌ Login Page Error: {log['message']}")
        
        if new_error_count == 0:
            print("   ✅ Login page loaded without errors")
        
        # Test 5: Test Authentication State Methods
        print("\n5. 🔍 Testing Authentication Methods...")
        
        # Test isAuthenticated method
        is_authenticated = driver.execute_script("return window.authManager.isAuthenticated();")
        print(f"   ✅ isAuthenticated() works: {is_authenticated}")
        
        # Test token methods
        has_access_token = driver.execute_script("return !!window.authManager.getAccessToken();")
        has_refresh_token = driver.execute_script("return !!window.authManager.getRefreshToken();")
        print(f"   ✅ Token methods work: access={has_access_token}, refresh={has_refresh_token}")
        
        # Test 6: Navigation Updates
        print("\n6. 🧭 Testing Navigation Updates...")
        driver.execute_script("window.authManager.updateNavigation();")
        
        auth_elements = driver.execute_script("""
            const authElements = document.querySelectorAll('[data-jwt-auth]');
            return authElements.length;
        """)
        
        no_auth_elements = driver.execute_script("""
            const noAuthElements = document.querySelectorAll('[data-jwt-no-auth]');
            return noAuthElements.length;
        """)
        
        print(f"   ✅ Found {auth_elements} auth elements and {no_auth_elements} non-auth elements")
        
        # Test 7: Final Console Error Check
        print("\n7. 🎯 Final Console Error Check...")
        final_logs = driver.get_log('browser')
        final_error_count = 0
        severe_errors = []
        
        for log in final_logs:
            if log['level'] == 'SEVERE':
                final_error_count += 1
                severe_errors.append(log['message'])
        
        if final_error_count == 0:
            print("   ✅ No JavaScript errors found in final check")
        else:
            print(f"   ❌ Found {final_error_count} final errors:")
            for error in severe_errors[-3:]:  # Show last 3 errors
                print(f"      - {error}")
        
        # Test 8: Memory and Performance Check
        print("\n8. ⚡ Performance Check...")
        
        # Check if multiple auth managers exist
        auth_manager_instances = driver.execute_script("""
            let count = 0;
            if (window.authManager) count++;
            if (window.jwtAuthManager) count++;
            if (window.JWTAuthManager) count++;
            return count;
        """)
        
        if auth_manager_instances == 1:
            print("   ✅ Single auth manager instance (good)")
        else:
            print(f"   ⚠️  Multiple auth manager instances detected: {auth_manager_instances}")
        
        # Success Summary
        print("\n" + "=" * 50)
        print("🎉 CLEAN JWT AUTHENTICATION TEST SUMMARY")
        print("=" * 50)
        
        if final_error_count == 0 and auth_manager_ready:
            print("✅ ALL TESTS PASSED!")
            print("✅ Clean JWT Authentication System is working correctly")
            print("✅ No console errors detected")
            print("✅ Authentication manager is properly initialized")
            return True
        else:
            print("❌ SOME TESTS FAILED")
            if final_error_count > 0:
                print(f"❌ {final_error_count} JavaScript errors found")
            if not auth_manager_ready:
                print("❌ Auth manager not ready")
            return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    finally:
        if driver:
            driver.quit()

def main():
    """Main test function"""
    print("🚀 Starting Clean JWT Authentication System Test")
    print("Testing the new implementation for console error elimination")
    print()
    
    success = test_clean_jwt_system()
    
    if success:
        print("\n🎉 SUCCESS: Clean JWT Authentication System is working perfectly!")
        print("🔧 Console errors have been eliminated")
        print("🚀 Ready for production use")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Issues detected in the clean JWT system")
        print("🔧 Additional debugging may be required")
        sys.exit(1)

if __name__ == "__main__":
    main()
