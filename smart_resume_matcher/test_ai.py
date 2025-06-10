# Test script for AI analyzer
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
from resumes.utils import AIAnalyzer

def test_ai():
    print("Testing AI Analyzer...")
    analyzer = AIAnalyzer()
    
    # Basic test with some resume text
    sample_text = """
    John Doe
    Software Developer
    
    EXPERIENCE
    Senior Software Developer, ABC Tech, 2020-2023
    - Developed web applications using Django and React
    - Led team of 3 developers for client projects
    - Improved performance of legacy systems by 40%
    
    Junior Developer, XYZ Software, 2018-2020
    - Worked on front-end development with HTML, CSS, and JavaScript
    - Implemented responsive design principles
    
    EDUCATION
    Bachelor of Science in Computer Science, University of Technology, 2018
    
    SKILLS
    Python, Django, React, JavaScript, HTML, CSS, SQL, Git
    """
    
    print("API Key status:", "Present" if settings.GROQ_API_KEY else "Missing")
    
    try:
        result = analyzer.analyze_resume(sample_text)
        print("Analysis successful!")
        print("Skills found:", result.get('skills', []))
        print("Experience level:", result.get('experience_level', 'Unknown'))
        print("Job titles:", result.get('job_titles', []))
        print("Summary:", result.get('summary', 'No summary'))
    except Exception as e:
        print(f"AI Analysis Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai()
