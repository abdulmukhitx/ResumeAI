#!/usr/bin/env python
import os
import sys
import json
import logging
from pprint import pprint

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from resumes.utils import AIAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fallback_analysis():
    """Test the fallback analysis functionality with various education formats"""
    analyzer = AIAnalyzer()
    
    # Test cases with different education formats
    test_cases = [
        """
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology
        2015-2019
        
        WORK EXPERIENCE
        Software Developer at ABC Corp
        2019-2022
        """,
        
        """
        EDUCATION
        MSc in Data Science, MIT, 2018
        BSc in Mathematics, Harvard University, 2016
        """,
        
        """
        QUALIFICATIONS
        Ph.D. in Artificial Intelligence from Stanford University (2017-2021)
        Master's degree in Computer Science, Berkeley, 2015
        """,
        
        """
        EDUCATIONAL BACKGROUND
        University of Washington
        B.S. in Information Technology
        2014
        """,
        
        """
        EDUCATION
        2018 - 2022: Bachelor of Business Administration
        Harvard Business School
        
        2022 - Present: MBA
        Stanford Graduate School of Business
        """
    ]
    
    print("----- TESTING EDUCATION EXTRACTION -----\n")
    
    for i, case in enumerate(test_cases):
        print(f"TEST CASE {i+1}:\n{case.strip()}\n")
        
        result = analyzer._fallback_analysis(case)
        print("EXTRACTED EDUCATION:")
        for edu in result["education"]:
            print(f"- {edu.get('degree', 'N/A')} | {edu.get('institution', 'N/A')} | {edu.get('year', 'N/A')}")
        
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    test_fallback_analysis()
