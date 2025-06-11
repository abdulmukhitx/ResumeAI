#!/usr/bin/env python
"""
Resume Analysis Tool for Smart Resume Matcher

This CLI tool allows you to analyze any resume PDF file using the Smart Resume Matcher AI analyzer.
It will show both the API-based and fallback analysis results for comparison.

Usage:
python analyze_resume.py /path/to/your/resume.pdf

Options:
--api-only: Only show API-based analysis
--fallback-only: Only show fallback analysis
--output=<file.json>: Save the analysis result to a JSON file
"""

import os
import sys
import json
import argparse
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_resume(pdf_path, api_only=False, fallback_only=False, output=None):
    """Analyze a resume PDF using the Smart Resume Matcher AI analyzer"""
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return
    
    if not pdf_path.lower().endswith('.pdf'):
        logger.error(f"Only PDF files are supported. Got: {pdf_path}")
        return
    
    analyzer = AIAnalyzer()
    
    # Extract text from PDF
    try:
        resume_text = analyzer.extract_text_from_pdf(pdf_path)
        logger.info(f"Successfully extracted text from {pdf_path}")
        logger.info(f"Text length: {len(resume_text)} characters")
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {str(e)}")
        return
    
    results = {}
    
    # API Analysis
    if not fallback_only:
        try:
            logger.info("Running API-based analysis...")
            api_result = analyzer.analyze_resume(resume_text)
            logger.info("API analysis completed")
            results['api'] = api_result
            
            print("\n===== API ANALYSIS RESULTS =====")
            print(f"Experience Level: {api_result.get('experience_level', 'Unknown')}")
            print(f"Confidence Score: {api_result.get('confidence_score', 0)}")
            print(f"Skills: {', '.join(api_result.get('skills', []))}")
            print(f"Job Titles: {', '.join(api_result.get('job_titles', []))}")
            print(f"Education: {len(api_result.get('education', []))} entries")
            print(f"Work Experience: {len(api_result.get('work_experience', []))} entries")
            print(f"Summary: {api_result.get('summary', 'No summary generated')}")
        except Exception as e:
            logger.error(f"API analysis failed: {str(e)}")
    
    # Fallback Analysis
    if not api_only:
        try:
            logger.info("Running fallback analysis...")
            fallback_result = analyzer._fallback_analysis(resume_text, "Manual test")
            logger.info("Fallback analysis completed")
            results['fallback'] = fallback_result
            
            print("\n===== FALLBACK ANALYSIS RESULTS =====")
            print(f"Experience Level: {fallback_result.get('experience_level', 'Unknown')}")
            print(f"Confidence Score: {fallback_result.get('confidence_score', 0)}")
            print(f"Skills: {', '.join(fallback_result.get('skills', []))}")
            print(f"Job Titles: {', '.join(fallback_result.get('job_titles', []))}")
            print(f"Education: {len(fallback_result.get('education', []))} entries")
            print(f"Summary: {fallback_result.get('summary', 'No summary generated')}")
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
    
    # Save output if requested
    if output and results:
        try:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output}")
        except Exception as e:
            logger.error(f"Failed to save results to {output}: {str(e)}")
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze a resume using Smart Resume Matcher')
    parser.add_argument('pdf_path', help='Path to the PDF resume file')
    parser.add_argument('--api-only', action='store_true', help='Only run API analysis')
    parser.add_argument('--fallback-only', action='store_true', help='Only run fallback analysis')
    parser.add_argument('--output', help='Save analysis results to JSON file')
    
    args = parser.parse_args()
    
    analyze_resume(args.pdf_path, args.api_only, args.fallback_only, args.output)
