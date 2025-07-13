#!/bin/bash

# Test different ways of sending the request to mimic browser behavior
echo "🔍 Testing browser-like requests..."

# Test 1: With referrer and user-agent headers
echo "Test 1: With browser-like headers"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
  -H "Referer: http://localhost:8000/login/" \
  -H "Origin: http://localhost:8000" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }'

echo -e "\n"

# Test 2: With X-Requested-With header (AJAX)
echo "Test 2: With X-Requested-With header"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }'

echo -e "\n"

# Test 3: With cookie header (simulate existing session)
echo "Test 3: With cookie header"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "Cookie: csrftoken=test; sessionid=test" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }'

echo -e "\n"

# Test 4: With CSRF token header
echo "Test 4: With CSRF token header"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: test-token" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }'

echo -e "\n"

# Test 5: Form-encoded data instead of JSON
echo "Test 5: Form-encoded data"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'email=abdulmukhit@kbtu.kz&password=password123'

echo -e "\n"
echo "✅ Browser-like tests complete!"
