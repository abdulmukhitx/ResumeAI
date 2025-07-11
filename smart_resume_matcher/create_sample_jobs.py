#!/usr/bin/env python3
"""
Create sample tech jobs for testing
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job

def create_sample_tech_jobs():
    """Create sample tech jobs for testing"""
    print("🏗️ Creating sample tech jobs...")
    
    tech_jobs = [
        {
            'hh_id': 999990001,  # Unique ID for our sample jobs
            'title': 'Senior Python Developer',
            'company_name': 'TechCorp Inc.',
            'description': '''We are looking for a Senior Python Developer to join our team. 
            The ideal candidate will have experience with Python, Django, Flask, SQL, 
            and modern web development practices. Experience with React and JavaScript is a plus.''',
            'requirements': 'Python, Django, Flask, SQL, PostgreSQL, REST APIs',
            'location': 'New York, NY',
            'salary_from': 120000,
            'salary_to': 160000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'experience_required': 'Senior level',
            'hh_url': 'https://example.com/job1',
            'is_active': True
        },
        {
            'hh_id': 999990002,
            'title': 'Full Stack JavaScript Developer',
            'company_name': 'WebSolutions LLC',
            'description': '''Join our dynamic team as a Full Stack Developer! You'll work with 
            React, Node.js, Express, and MongoDB to build amazing web applications. 
            Experience with TypeScript and modern CI/CD practices preferred.''',
            'requirements': 'JavaScript, React, Node.js, Express, MongoDB, TypeScript',
            'location': 'San Francisco, CA',
            'salary_from': 100000,
            'salary_to': 140000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'experience_required': 'Mid to Senior level',
            'hh_url': 'https://example.com/job2',
            'is_active': True
        },
        {
            'hh_id': 999990003,
            'title': 'React Frontend Developer',
            'company_name': 'StartupXYZ',
            'description': '''We need a talented React Developer to build user interfaces 
            for our cutting-edge applications. Must have strong skills in React, JavaScript, 
            HTML, CSS, and experience with modern frontend tools.''',
            'requirements': 'React, JavaScript, HTML, CSS, Webpack, Git',
            'location': 'Remote',
            'salary_from': 80000,
            'salary_to': 120000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'experience_required': 'Mid level',
            'hh_url': 'https://example.com/job3',
            'is_active': True
        },
        {
            'hh_id': 999990004,
            'title': 'DevOps Engineer',
            'company_name': 'CloudTech Solutions',
            'description': '''Looking for a DevOps Engineer to manage our cloud infrastructure. 
            Experience with AWS, Docker, Kubernetes, and CI/CD pipelines required. 
            Python scripting skills are highly valued.''',
            'requirements': 'AWS, Docker, Kubernetes, Python, Jenkins, Terraform',
            'location': 'Austin, TX',
            'salary_from': 110000,
            'salary_to': 150000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'experience_required': 'Senior level',
            'hh_url': 'https://example.com/job4',
            'is_active': True
        },
        {
            'hh_id': 999990005,
            'title': 'Junior Python Developer',
            'company_name': 'EduTech Inc.',
            'description': '''Great opportunity for a Junior Python Developer! You'll learn 
            and grow while working with Python, Django, and modern web technologies. 
            Perfect for recent graduates or career changers.''',
            'requirements': 'Python, Django, HTML, CSS, Basic SQL knowledge',
            'location': 'Chicago, IL',
            'salary_from': 60000,
            'salary_to': 80000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'experience_required': 'Entry level',
            'hh_url': 'https://example.com/job5',
            'is_active': True
        }
    ]
    
    created_count = 0
    for job_data in tech_jobs:
        job, created = Job.objects.get_or_create(
            title=job_data['title'],
            company_name=job_data['company_name'],
            defaults=job_data
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {job.title} at {job.company_name}")
        else:
            print(f"🔄 Already exists: {job.title} at {job.company_name}")
    
    print(f"\n🏁 Created {created_count} new tech jobs!")
    print(f"📊 Total active jobs now: {Job.objects.filter(is_active=True).count()}")

if __name__ == "__main__":
    create_sample_tech_jobs()
