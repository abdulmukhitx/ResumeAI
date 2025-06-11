#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import AIAnalyzer

def test_edu_extraction():
    """Test education extraction with mock resume"""
    analyzer = AIAnalyzer()
    
    with open('mock_resume.txt', 'r') as f:
        resume_text = f.read()
    
    # Run fallback analysis
    result = analyzer._fallback_analysis(resume_text)
    
    print("\nEXTRACTED EDUCATION:")
    for edu in result.get('education', []):
        print(f"- {edu.get('degree', 'N/A')} | {edu.get('institution', 'N/A')} | {edu.get('year', 'N/A')}")
    
    print("\nJOB TITLES:")
    print(', '.join(result.get('job_titles', ['None found'])))
    
    print("\nEXTRACTED SKILLS:")
    print(', '.join(result.get('skills', ['None found'])))
    
    print("\nEXPERIENCE LEVEL:")
    print(result.get('experience_level', 'Unknown'))
    
if __name__ == "__main__":
    test_edu_extraction()
