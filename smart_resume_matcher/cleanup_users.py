#!/usr/bin/env python
"""
Clean up duplicate usernames and emails in the database
"""

import os
import sys
import django

# Add the project path to Python path
project_path = os.path.abspath(os.path.dirname(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from django.db.models import Count, F
from django.db import models

def cleanup_duplicate_users():
    """Clean up duplicate users and fix username issues"""
    print("======== Cleaning up user database ========")
    
    # Find users with duplicate emails
    duplicate_emails = User.objects.values('email').annotate(
        count=Count('email')
    ).filter(count__gt=1)
    
    if duplicate_emails:
        print(f"Found {len(duplicate_emails)} duplicate email addresses:")
        for item in duplicate_emails:
            email = item['email']
            count = item['count']
            print(f"  - {email}: {count} users")
            
            # Keep the first user, delete the rest
            users_with_email = User.objects.filter(email=email).order_by('date_joined')
            users_to_delete = users_with_email[1:]  # All except the first
            
            for user in users_to_delete:
                print(f"    Deleting duplicate user: {user.username} ({user.email})")
                user.delete()
    
    # Find users with duplicate usernames
    duplicate_usernames = User.objects.values('username').annotate(
        count=Count('username')
    ).filter(count__gt=1)
    
    if duplicate_usernames:
        print(f"Found {len(duplicate_usernames)} duplicate usernames:")
        for item in duplicate_usernames:
            username = item['username']
            count = item['count']
            print(f"  - {username}: {count} users")
    
    # Fix users where username doesn't match email
    mismatched_users = []
    for user in User.objects.all():
        if user.username != user.email:
            mismatched_users.append(user)
    
    if mismatched_users:
        print(f"Found {len(mismatched_users)} users with mismatched username/email:")
        for user in mismatched_users:
            print(f"  - Updating {user.username} -> {user.email}")
            user.username = user.email
            user.save(update_fields=['username'])
    
    print("======== Cleanup complete ========")
    
    # Print summary
    total_users = User.objects.count()
    print(f"Total users in database: {total_users}")

if __name__ == '__main__':
    cleanup_duplicate_users()
