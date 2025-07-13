#!/bin/bash

# Comprehensive diagnostic test for the login issue
echo "🔍 Comprehensive Login Diagnostic Test"
echo "======================================"

# Check if server is running
echo "1. Checking server status..."
SERVER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$SERVER_STATUS" -eq 200 ]; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running or returning error: $SERVER_STATUS"
    exit 1
fi

# Test basic API endpoint
echo -e "\n2. Testing API endpoint accessibility..."
curl -s -X OPTIONS http://localhost:8000/api/auth/token/ -I
echo ""

# Test with different content types
echo -e "\n3. Testing with different content types..."

echo "3a. JSON content type:"
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}' \
  -w "\nHTTP Status: %{http_code}\n" | head -3

echo -e "\n3b. Form content type:"
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'email=abdulmukhit@kbtu.kz&password=password123' \
  -w "\nHTTP Status: %{http_code}\n" | head -3

echo -e "\n3c. With User-Agent header:"
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}' \
  -w "\nHTTP Status: %{http_code}\n" | head -3

# Test CSRF related issues
echo -e "\n4. Testing CSRF related issues..."

echo "4a. Without CSRF token:"
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}' \
  -w "\nHTTP Status: %{http_code}\n" | head -3

echo -e "\n4b. With fake CSRF token:"
curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: fake-token-123" \
  -d '{"email": "abdulmukhit@kbtu.kz", "password": "password123"}' \
  -w "\nHTTP Status: %{http_code}\n" | head -3

# Check database user status
echo -e "\n5. Checking database user status..."
cd /home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher
python manage.py shell -c "
from accounts.models import User
user = User.objects.get(email='abdulmukhit@kbtu.kz')
print(f'User ID: {user.id}')
print(f'Email: {user.email}')
print(f'Username: {user.username}')
print(f'Is Active: {user.is_active}')
print(f'Is Staff: {user.is_staff}')
print(f'Last Login: {user.last_login}')
print(f'Password Check: {user.check_password(\"password123\")}')
"

# Check authentication backend
echo -e "\n6. Testing authentication backend..."
python manage.py shell -c "
from django.contrib.auth import authenticate
user = authenticate(username='abdulmukhit@kbtu.kz', password='password123')
print(f'Auth result: {user}')
if user:
    print(f'Auth user email: {user.email}')
    print(f'Auth user active: {user.is_active}')
"

# Check serializer directly
echo -e "\n7. Testing serializer directly..."
python manage.py shell -c "
from accounts.serializers import CustomTokenObtainPairSerializer
data = {'email': 'abdulmukhit@kbtu.kz', 'password': 'password123'}
serializer = CustomTokenObtainPairSerializer(data=data)
print(f'Serializer valid: {serializer.is_valid()}')
if serializer.is_valid():
    result = serializer.validated_data
    print(f'Validation result: Access token present: {\"access\" in result}')
else:
    print(f'Serializer errors: {serializer.errors}')
"

echo -e "\n8. Testing view directly..."
python manage.py shell -c "
from accounts.jwt_views import CustomTokenObtainPairView
from django.test import RequestFactory
from django.http import JsonResponse
import json

factory = RequestFactory()
data = {'email': 'abdulmukhit@kbtu.kz', 'password': 'password123'}
request = factory.post('/api/auth/token/', 
                      data=json.dumps(data),
                      content_type='application/json')

view = CustomTokenObtainPairView()
view.request = request
view.format_kwarg = 'json'

try:
    response = view.post(request)
    print(f'View response status: {response.status_code}')
    if hasattr(response, 'data'):
        print(f'Response has data: {\"access\" in response.data}')
except Exception as e:
    print(f'View error: {e}')
"

echo -e "\n✅ Diagnostic complete!"
echo "If all tests pass, the issue is likely in the frontend JavaScript."
