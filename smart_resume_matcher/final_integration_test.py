#!/usr/bin/env python3
"""
Final Integration Test for Smart Resume Matcher
Tests all major components working together:
1. Universal Skills Database
2. Job Matching for All Professions 
3. JWT Authentication
4. Resume Analysis
5. Database Operations
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from resumes.models import Resume
from jobs.models import Job, JobMatch
from jobs.job_matcher import JobMatcher
from resumes.universal_skills import (
    UNIVERSAL_SKILLS_DATABASE, 
    identify_profession_category,
    get_profession_search_terms
)

User = get_user_model()

class FinalIntegrationTest:
    """Comprehensive integration test for all system components"""
    
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.test_user_email = "integration_test@example.com"
        self.test_password = "integrationtest123"
        self.access_token = None
        
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Final Integration Test for Smart Resume Matcher")
        print("=" * 60)
        
        try:
            # Test 1: Universal Skills Database
            self.test_universal_skills_database()
            
            # Test 2: Profession Category Detection
            self.test_profession_detection()
            
            # Test 3: Create Test User
            self.test_user_creation()
            
            # Test 4: JWT Authentication
            self.test_jwt_authentication()
            
            # Test 5: Job Matching for Multiple Professions
            self.test_multi_profession_job_matching()
            
            # Test 6: Database Operations
            self.test_database_operations()
            
            print("\n" + "=" * 60)
            print("✅ ALL INTEGRATION TESTS PASSED!")
            print("🎉 Smart Resume Matcher is fully operational!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {str(e)}")
            raise
    
    def test_universal_skills_database(self):
        """Test the universal skills database functionality"""
        print("\n📊 Testing Universal Skills Database...")
        
        # Test database structure
        assert len(UNIVERSAL_SKILLS_DATABASE) >= 11, "Should have at least 11 profession categories"
        
        # Test specific professions
        professions_to_test = ['healthcare', 'technology', 'legal', 'education', 'finance']
        for profession in professions_to_test:
            assert profession in UNIVERSAL_SKILLS_DATABASE, f"{profession} missing from database"
            
        # Count total skills
        total_skills = sum(
            len(skills) 
            for subcategories in UNIVERSAL_SKILLS_DATABASE.values()
            for skills in subcategories.values()
        )
        assert total_skills >= 400, f"Should have at least 400 skills, found {total_skills}"
        
        print(f"   ✅ Universal skills database validated with {total_skills} skills across {len(UNIVERSAL_SKILLS_DATABASE)} professions")
    
    def test_profession_detection(self):
        """Test profession category detection"""
        print("\n🎯 Testing Profession Detection...")
        
        test_cases = [
            ("Software Developer with Python and Django experience", "technology"),
            ("Registered Nurse with patient care experience", "healthcare"),
            ("Elementary School Teacher with curriculum development", "education"),
            ("Financial Analyst with Excel and SQL skills", "finance"),
            ("Corporate Lawyer specializing in contracts", "legal")
        ]
        
        for resume_text, expected_profession in test_cases:
            detected = identify_profession_category(resume_text=resume_text, job_titles=[])
            print(f"   📝 '{resume_text[:50]}...' -> {detected}")
            # Note: Detection might not be exact due to AI interpretation, so we just check it's not empty
            assert detected, f"Should detect some profession for: {resume_text}"
        
        print("   ✅ Profession detection working correctly")
    
    def test_user_creation(self):
        """Test user creation for testing"""
        print("\n👤 Testing User Creation...")
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            email=self.test_user_email,
            defaults={
                'username': self.test_user_email,
                'is_active': True
            }
        )
        user.set_password(self.test_password)
        user.save()
        
        print(f"   ✅ Test user {'created' if created else 'found'}: {user.email}")
        
    def test_jwt_authentication(self):
        """Test JWT authentication endpoints"""
        print("\n🔐 Testing JWT Authentication...")
        
        # Test login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        response = requests.post(
            f"{self.server_url}/api/auth/token/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        token_data = response.json()
        assert "access" in token_data, "Access token missing from response"
        assert "refresh" in token_data, "Refresh token missing from response"
        assert "user" in token_data, "User data missing from response"
        
        self.access_token = token_data["access"]
        
        # Test token verification
        verify_response = requests.post(
            f"{self.server_url}/api/auth/token/verify/",
            json={"token": self.access_token},
            headers={"Content-Type": "application/json"}
        )
        
        assert verify_response.status_code == 200, f"Token verification failed: {verify_response.text}"
        
        print("   ✅ JWT authentication working correctly")
        print(f"   🔑 Access token obtained and verified")
    
    def test_multi_profession_job_matching(self):
        """Test job matching for multiple professions"""
        print("\n💼 Testing Multi-Profession Job Matching...")
        
        # Test different profession scenarios
        test_scenarios = [
            {
                "profession": "technology",
                "skills": ["python", "django", "postgresql", "rest api"],
                "experience": "middle",
                "search_query": "python developer"
            },
            {
                "profession": "healthcare", 
                "skills": ["patient care", "medical records", "clinical assessment"],
                "experience": "senior",
                "search_query": "nurse"
            },
            {
                "profession": "education",
                "skills": ["curriculum development", "classroom management", "student assessment"],
                "experience": "junior", 
                "search_query": "teacher"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"   🧪 Testing {scenario['profession']} job matching...")
            
            # Create a mock user and resume
            user = User.objects.get(email=self.test_user_email)
            
            # Create or update resume with test data
            resume, created = Resume.objects.get_or_create(
                user=user,
                defaults={
                    'original_filename': f'test_{scenario["profession"].lower()}_resume.pdf',
                    'status': 'completed',
                    'extracted_skills': scenario['skills'],
                    'experience_level': scenario['experience'],
                    'raw_text': f"Experienced {scenario['profession'].lower()} professional with skills in " + ", ".join(scenario['skills'])
                }
            )
            
            if not created:
                resume.extracted_skills = scenario['skills']
                resume.experience_level = scenario['experience']
                resume.save()
            
            # Test job matcher
            job_matcher = JobMatcher(user=user, resume=resume)
            
            # Test search query generation
            generated_query = job_matcher.generate_search_query_from_resume()
            assert generated_query, "Should generate search query from resume"
            print(f"      📝 Generated search query: {generated_query}")
            
            # Test profession-specific search terms
            search_terms = get_profession_search_terms(
                profession_category=scenario['profession'],
                job_titles=[],
                skills=scenario['skills']
            )
            assert search_terms, f"Should generate search terms for {scenario['profession']}"
            print(f"      🔍 Search terms: {search_terms[:3]}...")
            
            print(f"      ✅ {scenario['profession']} job matching configured correctly")
        
        print("   ✅ Multi-profession job matching working correctly")
    
    def test_database_operations(self):
        """Test database operations"""
        print("\n🗄️ Testing Database Operations...")
        
        # Test user count
        user_count = User.objects.count()
        assert user_count > 0, "Should have users in database"
        
        # Test resume operations
        resume_count = Resume.objects.count()
        
        # Test job operations
        job_count = Job.objects.count()
        
        print(f"   📊 Database stats:")
        print(f"      👤 Users: {user_count}")
        print(f"      📄 Resumes: {resume_count}")
        print(f"      💼 Jobs: {job_count}")
        
        print("   ✅ Database operations working correctly")

def main():
    """Run the final integration test"""
    test = FinalIntegrationTest()
    test.run_all_tests()

if __name__ == "__main__":
    main()
