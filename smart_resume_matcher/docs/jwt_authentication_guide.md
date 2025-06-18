# JWT Authentication Implementation Guide

## Overview
This guide documents the complete JWT authentication system implemented for the Smart Resume Matcher application. The system provides secure, stateless authentication with token refresh, blacklisting, and enhanced user data responses.

## Features Implemented

### 1. JWT Token Configuration
- **Access Token Lifetime**: 1 hour
- **Refresh Token Lifetime**: 7 days  
- **Token Rotation**: Enabled (new refresh token on each refresh)
- **Token Blacklisting**: Enabled for secure logout
- **Custom Claims**: User email, name, and staff status embedded in tokens

### 2. Authentication Endpoints

#### `/api/auth/token/` - Enhanced Login
**Method**: POST  
**Purpose**: Login with enhanced user data response  
**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```
**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2025-06-17T18:27:18.773805Z",
    "last_login": "2025-06-17T18:39:36.048509Z",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "location": "New York, NY",
      "desired_position": "Software Engineer",
      "experience_level": "middle",
      "employment_types": ["full", "remote"],
      "preferred_locations": ["New York", "Remote"],
      "min_salary": 80000,
      "max_salary": 120000,
      "salary_currency": "USD",
      "is_job_search_active": true,
      "skills": ["Python", "Django", "JavaScript"],
      "full_name": "John Doe"
    },
    "latest_resume": {
      "id": 1,
      "filename": "resume.pdf",
      "uploaded_at": "2025-06-17T18:00:00Z",
      "skills_count": 15,
      "experience_level": "middle",
      "status": "completed"
    }
  }
}
```

#### `/api/auth/token/refresh/` - Token Refresh
**Method**: POST  
**Purpose**: Refresh access token with user data update  
**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### `/api/auth/token/verify/` - Token Verification
**Method**: POST  
**Purpose**: Verify token validity  
**Request**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Response**: `{}` (empty object if valid)

#### `/api/auth/logout/` - Secure Logout
**Method**: POST  
**Purpose**: Blacklist refresh token for secure logout  
**Request**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
**Response**:
```json
{
  "message": "Successfully logged out"
}
```

#### `/api/auth/user/` - Get User Profile
**Method**: GET  
**Purpose**: Get current authenticated user's profile  
**Headers**: `Authorization: Bearer <access_token>`  
**Response**: User profile data (same as login response user object)

#### `/api/auth/verify/` - Verify Token + Get User
**Method**: GET  
**Purpose**: Verify token and return user data  
**Headers**: `Authorization: Bearer <access_token>`  
**Response**:
```json
{
  "valid": true,
  "user": {
    // User profile data
  }
}
```

## Implementation Details

### 1. Settings Configuration
```python
# JWT Configuration in settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    # ... other settings
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # ... other settings
}
```

### 2. Custom Serializers
- **CustomTokenObtainPairSerializer**: Adds user profile data to login response
- **UserProfileSerializer**: Serializes complete user profile information

### 3. Custom Views
- **CustomTokenObtainPairView**: Enhanced login with user data
- **CustomTokenRefreshView**: Token refresh with user data updates
- **logout_view**: Secure logout with token blacklisting
- **user_profile_view**: Get authenticated user profile
- **verify_token_view**: Token verification with user data

### 4. Security Features
- Token blacklisting prevents reuse of logged-out tokens
- Token rotation provides fresh tokens on each refresh
- Custom claims include user identification data
- CSRF exemption for API endpoints
- Proper authentication classes configuration

## Database Changes
- `token_blacklist_outstandingtoken`: Tracks all issued tokens
- `token_blacklist_blacklistedtoken`: Tracks invalidated tokens

## Frontend Integration
For frontend applications, store tokens securely:

```javascript
// Store tokens after login
localStorage.setItem('access_token', response.access);
localStorage.setItem('refresh_token', response.refresh);
localStorage.setItem('user_data', JSON.stringify(response.user));

// Include token in API requests
fetch('/api/endpoint/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
});

// Handle token refresh
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    return data.access;
  }
  
  // Redirect to login if refresh fails
  window.location.href = '/login/';
}
```

## Testing
All endpoints have been tested and verified:
- ✅ Login with enhanced user data
- ✅ Token refresh with rotation
- ✅ Token verification
- ✅ Secure logout with blacklisting
- ✅ User profile retrieval
- ✅ Token verification with user data

## Next Steps
1. Frontend JavaScript integration
2. Automatic token refresh handling
3. Protected route middleware
4. User experience enhancements
