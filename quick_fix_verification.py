#!/usr/bin/env python3
"""
Quick fix verification for JWT auth and theme issues
"""

# Create a test HTML page to check auth manager
test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Quick Fix Test</title>
    <script src="/static/js/jwt_auth_clean.js"></script>
    <script>
        function checkAuth() {
            console.log('=== AUTH MANAGER CHECK ===');
            console.log('window.authManager exists:', !!window.authManager);
            
            if (window.authManager) {
                console.log('getAccessToken method exists:', typeof window.authManager.getAccessToken);
                console.log('isAuthenticated method exists:', typeof window.authManager.isAuthenticated);
                console.log('Current token:', window.authManager.getAccessToken() ? 'EXISTS' : 'NONE');
                console.log('Is authenticated:', window.authManager.isAuthenticated());
            } else {
                console.error('❌ window.authManager is not available!');
            }
        }
        
        window.addEventListener('load', function() {
            setTimeout(checkAuth, 500);
        });
    </script>
</head>
<body>
    <h1>Auth Manager Test</h1>
    <p>Check console for results</p>
    <button onclick="checkAuth()">Re-check Auth</button>
</body>
</html>
"""

with open('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/static/auth_test.html', 'w') as f:
    f.write(test_html)

print("✅ Created auth test page: http://localhost:8001/static/auth_test.html")
print("\n🔧 FIXES APPLIED:")
print("1. ✅ Fixed window.authManager initialization in jwt_auth_clean.js")
print("2. ⏳ Need to check theme toggle positioning")
print("\n📝 TO TEST:")
print("1. Visit: http://localhost:8001/static/auth_test.html")
print("2. Check console - should show authManager exists")
print("3. Try upload again: http://localhost:8001/jwt-resume-upload/")
print("4. Should no longer get 401 errors")
