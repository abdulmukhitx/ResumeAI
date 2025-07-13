#!/bin/bash

# Final Verification Test for Smart Resume Matcher
echo "🔍 Running final verification tests..."

# Test 1: Authentication API
echo "📋 Test 1: Authentication API"
response=$(curl -s -X POST "http://localhost:8000/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}')

if echo "$response" | grep -q "access"; then
    echo "✅ Authentication API working"
    access_token=$(echo "$response" | jq -r '.access')
else
    echo "❌ Authentication API failed"
    exit 1
fi

# Test 2: Login page loads
echo "📋 Test 2: Login page loads"
login_response=$(curl -s -X GET "http://localhost:8000/login/" -H "Accept: text/html")

if echo "$login_response" | grep -q "Welcome Back"; then
    echo "✅ Login page loads correctly"
else
    echo "❌ Login page failed to load"
    exit 1
fi

# Test 3: Job matches page redirects properly
echo "📋 Test 3: Job matches page authentication"
job_response=$(curl -s -I -X GET "http://localhost:8000/jobs/ai-matches/" -H "Accept: text/html")

if echo "$job_response" | grep -q "302\|Location.*login"; then
    echo "✅ Job matches page redirects to login (expected for unauthenticated)"
else
    echo "❌ Job matches page redirect failed"
    exit 1
fi

# Test 4: Auto-match API with authentication
echo "📋 Test 4: Auto-match API with authentication"
if [ -n "$access_token" ]; then
    auto_match_response=$(curl -s -X GET "http://localhost:8000/jobs/ai-matches/?auto_match=true" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer $access_token" \
      -H "X-Requested-With: XMLHttpRequest")
    
    if echo "$auto_match_response" | grep -q "success"; then
        echo "✅ Auto-match API working"
    else
        echo "❌ Auto-match API failed"
        exit 1
    fi
else
    echo "❌ No access token available for auto-match test"
    exit 1
fi

echo ""
echo "🎉 All tests passed! The Smart Resume Matcher is working correctly."
echo "🚀 Ready for production deployment!"
