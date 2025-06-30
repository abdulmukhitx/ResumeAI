#!/usr/bin/env python3
"""
Simple End-to-End Test for Modern Resume Processing System
==========================================================

This script creates a simple text file with resume content and tests the complete
modern processing pipeline to ensure everything works end-to-end.
"""

import os
import sys
import logging
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from modern_resume_processor import ModernResumeProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_end_to_end():
    """Test the complete modern processing system end-to-end."""
    
    # Create a comprehensive test resume
    test_resume_content = """
JOHN DOE
Senior Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 8+ years of experience in full-stack development.
Expert in Python, JavaScript, and cloud technologies. Led multiple successful projects
and teams in fast-paced startup environments.

EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2020 - Present
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipelines reducing deployment time by 70%
• Mentored team of 5 junior developers
• Technologies: Python, Django, React, AWS, Docker, Kubernetes

Software Engineer | StartupXYZ | 2018 - 2020
• Developed RESTful APIs using Flask and PostgreSQL
• Built responsive front-end applications using React and Redux
• Integrated third-party payment systems (Stripe, PayPal)
• Improved application performance by 40% through optimization

Junior Developer | WebDev Solutions | 2016 - 2018
• Created dynamic websites using HTML, CSS, JavaScript, and PHP
• Maintained MySQL databases and wrote optimized queries
• Collaborated with design team to implement user interfaces
• Participated in agile development processes

EDUCATION

Master of Science in Computer Science
Stanford University, 2016
GPA: 3.8/4.0

Bachelor of Science in Software Engineering  
University of California, Berkeley, 2014
GPA: 3.7/4.0

TECHNICAL SKILLS

Programming Languages: Python, JavaScript, TypeScript, Java, C++, PHP, SQL
Frameworks: Django, Flask, React, Redux, Node.js, Express, Spring Boot
Databases: PostgreSQL, MySQL, MongoDB, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitLab CI/CD
Tools: Git, JIRA, Confluence, VS Code, IntelliJ IDEA

CERTIFICATIONS
• AWS Certified Solutions Architect (2022)
• Certified Kubernetes Administrator (2021)
• Google Cloud Professional Developer (2020)

PROJECTS

E-commerce Platform (2022)
• Full-stack web application with payment processing
• Tech stack: React, Django, PostgreSQL, AWS
• Handled 10k+ concurrent users

Real-time Chat Application (2021)
• WebSocket-based messaging system
• Tech stack: Node.js, Socket.io, Redis, Docker
• Deployed on Kubernetes cluster

LANGUAGES
• English (Native)
• Spanish (Conversational)
• French (Basic)
"""

    # Save to a temporary file
    test_file_path = "/tmp/test_resume_comprehensive.txt"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_resume_content)
    
    print("=" * 60)
    print("MODERN RESUME PROCESSING SYSTEM - END-TO-END TEST")
    print("=" * 60)
    
    try:
        # Initialize processor
        processor = ModernResumeProcessor()
        print("✓ Modern Resume Processor initialized")
        
        # Process the resume
        print("\nProcessing comprehensive test resume...")
        result = processor.process_resume(test_file_path)
        
        print(f"\nPROCESSING RESULTS:")
        print(f"Overall Success: {result.success}")
        print(f"Processing Method: {result.processing_method}")
        print(f"Extraction Method: {result.extraction_method}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Resume Score: {result.resume_score:.1f}")
        
        print(f"\nEXTRACTED DATA:")
        print(f"Text Length: {len(result.extracted_text)} characters")
        print(f"Skills Found: {len(result.skills)}")
        print(f"Experience Level: {result.experience_level}")
        print(f"Job Titles: {len(result.job_titles)}")
        print(f"Education Entries: {len(result.education)}")
        print(f"Work Experience: {len(result.work_experience)}")
        
        if result.skills:
            print(f"\nTOP SKILLS IDENTIFIED:")
            for i, skill in enumerate(result.skills[:10], 1):
                print(f"  {i}. {skill}")
        
        if result.job_titles:
            print(f"\nJOB TITLES IDENTIFIED:")
            for i, title in enumerate(result.job_titles[:5], 1):
                print(f"  {i}. {title}")
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"PDF Processing Time: {result.pdf_processing_time:.2f}s")
        print(f"AI Processing Time: {result.ai_processing_time:.2f}s")
        print(f"Total Processing Time: {result.total_processing_time:.2f}s")
        
        if result.processing_errors or result.pdf_errors or result.ai_errors:
            print(f"\nERRORS:")
            all_errors = result.processing_errors + result.pdf_errors + result.ai_errors
            for i, error in enumerate(all_errors[:5], 1):
                print(f"  {i}. {error}")
        
        if result.processing_warnings or result.pdf_warnings or result.ai_warnings:
            print(f"\nWARNINGS:")
            all_warnings = result.processing_warnings + result.pdf_warnings + result.ai_warnings
            for i, warning in enumerate(all_warnings[:5], 1):
                print(f"  {i}. {warning}")
        
        # Test the simplified interface
        print(f"\nTESTING SIMPLIFIED INTERFACE:")
        simple_result = processor.process_resume_safe(test_file_path)
        print(f"Simplified Success: {simple_result['success']}")
        print(f"Simplified Method: {simple_result['method']}")
        print(f"Simplified Confidence: {simple_result['confidence']:.2f}")
        
        # Get processing statistics
        print(f"\nPROCESSING STATISTICS:")
        stats = processor.get_processing_statistics()
        print(f"Total Processed: {stats['processing_stats']['total_processed']}")
        print(f"Successful Extractions: {stats['processing_stats']['successful_extractions']}")
        print(f"Successful Analyses: {stats['processing_stats']['successful_analyses']}")
        
        # Overall assessment
        print(f"\n" + "=" * 60)
        if result.success and result.confidence_score > 0.5:
            print("🎉 END-TO-END TEST PASSED!")
            print("The modern resume processing system is working correctly.")
        elif result.success:
            print("⚠️  END-TO-END TEST PARTIALLY PASSED")
            print("Processing succeeded but with low confidence.")
        else:
            print("❌ END-TO-END TEST FAILED")
            print("Processing failed - please check the errors above.")
        
        print("=" * 60)
        
        # Clean up
        os.remove(test_file_path)
        
        return result.success
        
    except Exception as e:
        print(f"❌ END-TO-END TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        
        return False

if __name__ == '__main__':
    success = test_end_to_end()
    sys.exit(0 if success else 1)
