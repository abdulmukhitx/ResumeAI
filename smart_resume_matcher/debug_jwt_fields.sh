#!/bin/bash

# Debug JWT Login - Test different field combinations
echo "🔍 Testing JWT Login with different field combinations..."

# Test 1: Current way (email + password)
echo "Test 1: email + password"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }' \
  --verbose

echo -e "\n" 

# Test 2: Try with username field instead
echo "Test 2: username + password"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }' \
  --verbose

echo -e "\n"

# Test 3: Try with both fields
echo "Test 3: both email and username + password"
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "abdulmukhit@kbtu.kz",
    "username": "abdulmukhit@kbtu.kz",
    "password": "password123"
  }' \
  --verbose

echo -e "\n"

# Test 4: Check what the user model actually expects
echo "Test 4: Check user model USERNAME_FIELD"
cd /home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher
python manage.py shell -c "
from accounts.models import User
print('USERNAME_FIELD:', User.USERNAME_FIELD)
print('REQUIRED_FIELDS:', User.REQUIRED_FIELDS)
user = User.objects.get(email='abdulmukhit@kbtu.kz')
print('User username:', user.username)
print('User email:', user.email)
print('User is_active:', user.is_active)
"

echo -e "\n"
echo "✅ Debug complete!"
