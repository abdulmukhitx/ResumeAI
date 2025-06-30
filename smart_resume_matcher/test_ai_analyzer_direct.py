#!/usr/bin/env python3
"""
Direct AI Analyzer Test for Modern Resume Processing System
==========================================================

This script directly tests the AI analyzer component with text content
to verify the core analysis functionality works correctly.
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

from modern_ai_analyzer import ModernAIAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_analyzer_direct():
    """Test the AI analyzer directly with text content."""
    
    # Create a comprehensive test resume
    test_resume_text = """
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

    print("=" * 60)
    print("MODERN AI ANALYZER - DIRECT TEST")
    print("=" * 60)
    
    try:
        # Initialize AI analyzer
        analyzer = ModernAIAnalyzer()
        print("✓ Modern AI Analyzer initialized")
        
        # Analyze the resume text
        print("\nAnalyzing comprehensive test resume...")
        result = analyzer.analyze_resume_comprehensive(test_resume_text)
        
        print(f"\nANALYSIS RESULTS:")
        print(f"Success: {result.success}")
        print(f"Processing Method: {result.processing_method}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Resume Score: {result.resume_score:.1f}")
        
        print(f"\nEXTRACTED DATA:")
        print(f"Skills Found: {len(result.skills)}")
        print(f"Experience Level: {result.experience_level}")
        print(f"Education Entries: {len(result.education)}")
        print(f"Work Experience: {len(result.work_experience)}")
        print(f"Primary Industry: {result.primary_industry}")
        print(f"Total Experience Years: {result.total_experience_years}")
        
        if result.skills:
            print(f"\nTOP SKILLS IDENTIFIED:")
            for i, skill in enumerate(result.skills[:15], 1):
                print(f"  {i}. {skill}")
        
        if result.work_experience:
            print(f"\nWORK EXPERIENCE IDENTIFIED:")
            for i, exp in enumerate(result.work_experience, 1):
                print(f"  {i}. {exp.title} at {exp.company}")
        
        if result.education:
            print(f"\nEDUCATION IDENTIFIED:")
            for i, edu in enumerate(result.education, 1):
                print(f"  {i}. {edu}")
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"Processing Time: {result.processing_time:.2f}s")
        
        if result.errors:
            print(f"\nERRORS:")
            for i, error in enumerate(result.errors[:5], 1):
                print(f"  {i}. {error}")
        
        if result.warnings:
            print(f"\nWARNINGS:")
            for i, warning in enumerate(result.warnings[:5], 1):
                print(f"  {i}. {warning}")
        
        # Get analyzer statistics
        print(f"\nANALYZER STATISTICS:")
        stats = analyzer.get_analysis_statistics()
        print(f"Total Analyzed: {stats.get('total_analyzed', 0)}")
        print(f"Successful Analyses: {stats.get('successful_analyses', 0)}")
        print(f"Available Providers: {len(analyzer.ai_providers)}")
        
        # Overall assessment
        print(f"\n" + "=" * 60)
        if result.success and result.confidence_score > 0.5 and len(result.skills) > 5:
            print("🎉 AI ANALYZER TEST PASSED!")
            print("The modern AI analyzer is working correctly.")
            print(f"Successfully identified {len(result.skills)} skills and {len(result.work_experience)} work experiences.")
        elif result.success:
            print("⚠️  AI ANALYZER TEST PARTIALLY PASSED")
            print("Analysis succeeded but with limited results.")
        else:
            print("❌ AI ANALYZER TEST FAILED")
            print("Analysis failed - please check the errors above.")
        
        print("=" * 60)
        
        return result.success and len(result.skills) > 0
        
    except Exception as e:
        print(f"❌ AI ANALYZER TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ai_analyzer_direct()
    sys.exit(0 if success else 1)
