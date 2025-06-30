#!/usr/bin/env python3
"""
Test the JWT auth getAccessToken fix
"""

# Create a simple test to verify the auth manager works
test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>JWT Auth Test</title>
    <script src="/static/js/jwt_auth_clean.js"></script>
    <script>
        function testAuthManager() {
            console.log('Testing JWT Auth Manager...');
            
            // Check if auth manager is available
            if (window.authManager) {
                console.log('✅ window.authManager is available');
                
                // Test getAccessToken method
                if (typeof window.authManager.getAccessToken === 'function') {
                    console.log('✅ getAccessToken method exists');
                    const token = window.authManager.getAccessToken();
                    console.log('Current token:', token ? 'Token exists' : 'No token');
                } else {
                    console.error('❌ getAccessToken method not found');
                }
                
                // Test isAuthenticated method
                if (typeof window.authManager.isAuthenticated === 'function') {
                    console.log('✅ isAuthenticated method exists');
                    console.log('Is authenticated:', window.authManager.isAuthenticated());
                } else {
                    console.error('❌ isAuthenticated method not found');
                }
            } else {
                console.error('❌ window.authManager not found');
            }
        }
        
        // Test when page loads
        window.addEventListener('load', function() {
            // Wait a moment for auth manager to initialize
            setTimeout(testAuthManager, 100);
        });
    </script>
</head>
<body>
    <h1>JWT Auth Manager Test</h1>
    <p>Check console for test results.</p>
</body>
</html>
"""

with open('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/static/jwt_auth_test.html', 'w') as f:
    f.write(test_html)

print("✅ Created JWT auth test page")
print("Visit: http://localhost:8001/static/jwt_auth_test.html")
print("\n🔧 FIXED: Updated resume upload template to use getAccessToken() instead of getToken()")
print("🔧 The error 'window.authManager.getToken is not a function' should now be resolved!")
print("\nNext steps:")
print("1. Test the upload at: http://localhost:8001/jwt-resume-upload/")
print("2. The upload should now work without console errors")
print("3. Files should be properly uploaded and analyzed")
