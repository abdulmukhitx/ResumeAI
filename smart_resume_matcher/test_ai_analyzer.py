#!/usr/bin/env python
"""
Test script for AI Analyzer in Smart Resume Matcher
This script tests both the API-based and fallback analysis methods
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from resumes.utils import AIAnalyzer
from django.conf import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ai_analysis():
    """Test the AI analysis functionality"""
    sample_resume = """
    JOHN DOE
    Software Developer
    john.doe@example.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

    SUMMARY
    Experienced Software Developer with 5 years of experience specializing in Python, Django, and React.
    Strong background in developing RESTful APIs and implementing cloud-based solutions.

    SKILLS
    Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
    Frameworks: Django, Flask, React, Redux, Express.js
    Tools: Git, Docker, Kubernetes, AWS, Azure
    Databases: PostgreSQL, MongoDB, Redis

    WORK EXPERIENCE
    Senior Software Developer
    ABC Technologies, New York, NY
    January 2020 - Present
    • Developed and maintained RESTful APIs using Django REST Framework
    • Implemented authentication and authorization modules using JWT
    • Optimized database queries resulting in 40% faster application response time
    • Led a team of 4 developers for the customer portal project

    Software Developer
    XYZ Solutions, San Francisco, CA
    March 2018 - December 2019
    • Built responsive web applications using React and Redux
    • Created automated test suites with Jest and Cypress
    • Collaborated with UX/UI designers to implement new features
    • Participated in agile development processes

    EDUCATION
    Master of Science in Computer Science
    Stanford University, Stanford, CA
    Graduated: May 2018

    Bachelor of Science in Software Engineering
    University of California, Berkeley
    Graduated: June 2016
    """
    
    analyzer = AIAnalyzer()
    
    # Test 1: Test with API (if key is available)
    logger.info("Testing AI analysis with API...")
    try:
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key':
            api_result = analyzer.analyze_resume(sample_resume)
            logger.info(f"API analysis result: {json.dumps(api_result, indent=2)}")
            logger.info("API analysis test: PASSED" if api_result.get("skills") else "API analysis test: FAILED")
        else:
            logger.warning("Skipping API test - No valid API key configured")
            logger.info("To run API tests, set a valid GROQ_API_KEY in your settings")
    except Exception as e:
        logger.error(f"API analysis test FAILED with error: {str(e)}")
    
    # Test 2: Test fallback analysis
    logger.info("\nTesting fallback analysis...")
    try:
        # Force fallback by directly calling the method
        fallback_result = analyzer._fallback_analysis(sample_resume, "Test forced fallback")
        logger.info(f"Fallback analysis result: {json.dumps(fallback_result, indent=2)}")
        logger.info("Fallback analysis test: PASSED" if fallback_result.get("skills") else "Fallback analysis test: FAILED")
    except Exception as e:
        logger.error(f"Fallback analysis test FAILED with error: {str(e)}")

if __name__ == '__main__':
    test_ai_analysis()
