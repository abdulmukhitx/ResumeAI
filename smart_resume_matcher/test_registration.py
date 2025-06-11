#!/usr/bin/env python
"""
Test user registration to ensure the IntegrityError is fixed
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse

# Add the project path to Python path
project_path = os.path.abspath(os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from accounts.forms import UserRegistrationForm

def test_registration_form():
    """Test the registration form validation"""
    print("======== Testing Registration Form ========")
    
    # Test valid form data
    valid_data = {
        'email': 'newuser@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'password1': 'ComplexPassword123!',
        'password2': 'ComplexPassword123!'
    }
    
    form = UserRegistrationForm(data=valid_data)
    if form.is_valid():
        print("✓ Form validation passed")
        try:
            user = form.save()
            print(f"✓ User created successfully: {user.email}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Name: {user.first_name} {user.last_name}")
        except Exception as e:
            print(f"✗ Error saving user: {e}")
    else:
        print("✗ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
    
    # Test duplicate email
    print("\n--- Testing duplicate email handling ---")
    duplicate_data = {
        'email': 'newuser@example.com',  # Same email as above
        'first_name': 'Another',
        'last_name': 'User',
        'password1': 'AnotherPassword123!',
        'password2': 'AnotherPassword123!'
    }
    
    form = UserRegistrationForm(data=duplicate_data)
    if form.is_valid():
        print("✗ Form should have failed validation for duplicate email")
    else:
        print("✓ Form correctly rejected duplicate email")
        if 'email' in form.errors:
            print(f"  - Email error: {form.errors['email']}")

def test_user_creation():
    """Test direct user creation"""
    print("\n======== Testing Direct User Creation ========")
    
    try:
        # Create user directly
        user = User.objects.create_user(
            email='directuser@example.com',
            username='directuser@example.com',
            password='TestPassword123!',
            first_name='Direct',
            last_name='User'
        )
        print(f"✓ Direct user creation successful: {user.email}")
        print(f"  - Username: {user.username}")
        print(f"  - Email matches username: {user.username == user.email}")
        
    except Exception as e:
        print(f"✗ Direct user creation failed: {e}")

def test_authentication():
    """Test user authentication with email"""
    print("\n======== Testing Authentication ========")
    
    from django.contrib.auth import authenticate
    
    # Test with existing user
    user = User.objects.first()
    if user:
        # Test authentication with email
        auth_user = authenticate(username=user.email, password='password123')  # Default password from cleanup
        if auth_user:
            print(f"✓ Authentication successful for: {user.email}")
        else:
            print(f"✗ Authentication failed for: {user.email}")
            print("  (This might be expected if password was changed)")

def main():
    print("Testing user registration system fixes...\n")
    
    # Show current user count
    user_count = User.objects.count()
    print(f"Current users in database: {user_count}")
    
    if user_count > 0:
        print("Existing users:")
        for user in User.objects.all():
            print(f"  - {user.email} (username: {user.username})")
    
    print()
    
    test_registration_form()
    test_user_creation()
    test_authentication()
    
    print(f"\n======== Test Complete ========")
    print(f"Total users after tests: {User.objects.count()}")

if __name__ == '__main__':
    main()
