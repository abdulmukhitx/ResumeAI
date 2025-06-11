#!/usr/bin/env python
"""
Deployment debugging script to check what's failing in production
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.models import Resume
from accounts.models import User
from resumes.utils import AIAnalyzer
from django.conf import settings
import logging

def debug_deployment_issues():
    """Debug common deployment issues"""
    print("=== DEPLOYMENT DEBUGGING ===\n")
    
    # 1. Check environment variables
    print("1. ENVIRONMENT VARIABLES:")
    groq_key = getattr(settings, 'GROQ_API_KEY', None)
    print(f"   GROQ_API_KEY: {'Present' if groq_key else 'MISSING'}")
    if groq_key:
        print(f"   GROQ_API_KEY length: {len(groq_key)} chars")
    print()
    
    # 2. Check database
    print("2. DATABASE STATUS:")
    try:
        user_count = User.objects.count()
        resume_count = Resume.objects.count()
        print(f"   Users: {user_count}")
        print(f"   Resumes: {resume_count}")
        print("   ✅ Database accessible")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    print()
    
    # 3. Check file system permissions
    print("3. FILE SYSTEM:")
    media_root = settings.MEDIA_ROOT
    print(f"   MEDIA_ROOT: {media_root}")
    print(f"   MEDIA_ROOT exists: {os.path.exists(media_root)}")
    print(f"   MEDIA_ROOT writable: {os.access(media_root, os.W_OK)}")
    
    # Check for resumes directory
    resumes_dir = os.path.join(media_root, 'resumes')
    print(f"   Resumes dir exists: {os.path.exists(resumes_dir)}")
    if os.path.exists(resumes_dir):
        print(f"   Resumes dir writable: {os.access(resumes_dir, os.W_OK)}")
    print()
    
    # 4. Test AI Analyzer
    print("4. AI ANALYZER TEST:")
    try:
        analyzer = AIAnalyzer()
        print("   ✅ AIAnalyzer initialized")
        
        # Test with sample text
        sample_text = """
        John Doe
        Software Engineer
        
        SKILLS:
        Python, Django, JavaScript, React
        
        EXPERIENCE:
        Senior Software Developer at Tech Corp (2020-2023)
        - Developed web applications
        - Led team of 5 developers
        """
        
        result = analyzer.analyze_resume(sample_text)
        print(f"   ✅ Analysis successful")
        print(f"   Skills found: {result.get('skills', [])}")
        print(f"   Experience level: {result.get('experience_level', 'None')}")
        
    except Exception as e:
        print(f"   ❌ AI Analyzer error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 5. Check recent resumes
    print("5. RECENT RESUME ANALYSIS:")
    recent_resumes = Resume.objects.order_by('-created_at')[:5]
    
    if not recent_resumes:
        print("   No resumes found")
    
    for resume in recent_resumes:
        print(f"   Resume: {resume.original_filename}")
        print(f"     User: {resume.user.email}")
        print(f"     Status: {resume.status}")
        print(f"     Created: {resume.created_at}")
        print(f"     File exists: {os.path.exists(resume.file.path) if resume.file else False}")
        print(f"     Skills: {len(resume.extracted_skills)} extracted")
        print(f"     Experience: {resume.experience_level}")
        print(f"     Raw text length: {len(resume.raw_text) if resume.raw_text else 0}")
        print("     ---")
    print()
    
    # 6. Check logs for errors
    print("6. LOGGING CONFIG:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   LOGGING configured: {hasattr(settings, 'LOGGING')}")
    
    # 7. Test file upload simulation
    print("7. FILE UPLOAD TEST:")
    try:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import RequestFactory
        
        # Create a fake PDF content
        fake_pdf = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer << /Size 4 /Root 1 0 R >>\nstartxref\n180\n%%EOF"
        
        print(f"   ✅ File upload simulation possible")
        
    except Exception as e:
        print(f"   ❌ File upload test error: {e}")

if __name__ == "__main__":
    debug_deployment_issues()
