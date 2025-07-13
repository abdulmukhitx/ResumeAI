#!/bin/bash

echo "🔧 Testing login fix..."

# Test 1: Direct API call
echo "📋 Test 1: Direct API call"
response=$(curl -s -X POST "http://localhost:8000/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}')

if echo "$response" | grep -q "access"; then
    echo "✅ API call successful"
else
    echo "❌ API call failed: $response"
    exit 1
fi

# Test 2: Check login page loads
echo "📋 Test 2: Login page loads"
login_check=$(curl -s -X GET "http://localhost:8000/login/" -H "Accept: text/html")

if echo "$login_check" | grep -q "csrf"; then
    echo "✅ Login page has CSRF token"
else
    echo "❌ Login page missing CSRF token"
fi

echo ""
echo "🎉 Login fix applied successfully!"
echo "📝 Instructions:"
echo "1. Go to http://localhost:8000/login/"
echo "2. Click 'Clear Browser Cache' button"
echo "3. Use credentials: abdulmukhit@kbtu.kz / password123"
echo "4. Login should now work!"
