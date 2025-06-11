#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path
import re

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import AIAnalyzer

def debug_edu_extraction():
    """Debug the education extraction with detailed output"""
    analyzer = AIAnalyzer()
    
    with open('mock_resume.txt', 'r') as f:
        resume_text = f.read()
    
    print("\n==== EDUCATION SECTION EXTRACTION DEBUG ====")
    # Try to find the education section
    edu_section_match = re.search(r'(?:EDUCATION|ACADEMIC|QUALIFICATIONS|EDUCATIONAL BACKGROUND)[^\n]*\n(.*?)(?:\n\n|\n[A-Z]{2,}|\Z)', 
                                resume_text, re.IGNORECASE | re.DOTALL)
    
    if edu_section_match:
        edu_section = edu_section_match.group(1)
        print(f"Found education section: {len(edu_section)} chars")
        print("CONTENT:")
        print(edu_section)
    else:
        print("No education section found using regex pattern!")
    
    # Find universities
    university_pattern = r'((?:University|College|Institute|School)[^,\n]*|MIT|Stanford|Harvard|Berkeley)'
    universities = re.findall(university_pattern, resume_text, re.IGNORECASE)
    
    print("\nFOUND UNIVERSITIES:")
    for uni in universities:
        print(f"- {uni}")
    
    # Extract degrees
    degree_pattern = r'\b(bachelor|master|phd|doctorate|mba|bs|ba|ms|ma|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?)\b'
    degrees = re.findall(degree_pattern, resume_text, re.IGNORECASE)
    
    print("\nFOUND DEGREE TERMS:")
    for degree in degrees:
        print(f"- {degree}")
    
    # Extract years
    year_pattern = r'(\d{4}(?:\s*[-–]\s*(?:\d{4}|present|ongoing|current))?)'
    years = re.findall(year_pattern, resume_text)
    
    print("\nFOUND YEAR PATTERNS:")
    for year in years:
        print(f"- {year}")
    
    # Run the complete analysis
    print("\n==== RUNNING FULL FALLBACK ANALYSIS ====")
    result = analyzer._fallback_analysis(resume_text)
    
    print("\nFINAL EXTRACTED EDUCATION:")
    if result.get('education'):
        for edu in result['education']:
            print(f"- {edu.get('degree', 'N/A')} | {edu.get('institution', 'N/A')} | {edu.get('year', 'N/A')}")
    else:
        print("No education entries found in final result!")

if __name__ == "__main__":
    debug_edu_extraction()
