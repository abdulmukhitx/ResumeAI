#!/usr/bin/env python
"""
Test script to demonstrate enhanced PDF processing with various PDF types
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import PDFProcessor
from resumes.enhanced_analyzer import EnhancedAIAnalyzer
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_complex_test_pdf(pdf_path):
    """Create a more complex test PDF with various layouts"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter
        
        # Page 1: Standard resume format
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 80, "Sarah Johnson")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 100, "Senior Full-Stack Developer")
        c.drawString(100, height - 120, "📧 sarah.johnson@techcorp.com | 📱 (555) 987-6543")
        c.drawString(100, height - 140, "🔗 linkedin.com/in/sarahjohnson | 🌐 github.com/sarahjdev")
        
        # Professional Summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, height - 180, "PROFESSIONAL SUMMARY")
        c.line(100, height - 185, 500, height - 185)
        
        c.setFont("Helvetica", 10)
        summary_text = [
            "Experienced Senior Full-Stack Developer with 8+ years of expertise in Python, JavaScript,",
            "React, Django, and cloud technologies. Led development teams of 5+ engineers and delivered",
            "scalable web applications serving 100k+ users. Strong background in machine learning,",
            "DevOps practices, and agile methodologies."
        ]
        
        y_pos = height - 200
        for line in summary_text:
            c.drawString(120, y_pos, line)
            y_pos -= 15
        
        # Technical Skills (in columns)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_pos - 20, "TECHNICAL SKILLS")
        c.line(100, y_pos - 25, 500, y_pos - 25)
        
        c.setFont("Helvetica-Bold", 10)
        y_pos -= 45
        
        # Column 1
        c.drawString(120, y_pos, "Programming Languages:")
        c.setFont("Helvetica", 10)
        c.drawString(120, y_pos - 15, "• Python (8 years)")
        c.drawString(120, y_pos - 30, "• JavaScript/TypeScript (7 years)")
        c.drawString(120, y_pos - 45, "• Java (5 years)")
        c.drawString(120, y_pos - 60, "• Go (3 years)")
        c.drawString(120, y_pos - 75, "• C++ (4 years)")
        
        # Column 2
        c.setFont("Helvetica-Bold", 10)
        c.drawString(320, y_pos, "Frameworks & Libraries:")
        c.setFont("Helvetica", 10)
        c.drawString(320, y_pos - 15, "• Django/Django REST Framework")
        c.drawString(320, y_pos - 30, "• React.js/Next.js/Redux")
        c.drawString(320, y_pos - 45, "• Node.js/Express.js")
        c.drawString(320, y_pos - 60, "• FastAPI/Flask")
        c.drawString(320, y_pos - 75, "• TensorFlow/PyTorch")
        
        y_pos -= 100
        c.setFont("Helvetica-Bold", 10)
        c.drawString(120, y_pos, "Databases & Storage:")
        c.setFont("Helvetica", 10)
        c.drawString(120, y_pos - 15, "• PostgreSQL/MySQL")
        c.drawString(120, y_pos - 30, "• MongoDB/Redis")
        c.drawString(120, y_pos - 45, "• Elasticsearch")
        c.drawString(120, y_pos - 60, "• AWS S3/DynamoDB")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(320, y_pos, "Cloud & DevOps:")
        c.setFont("Helvetica", 10)
        c.drawString(320, y_pos - 15, "• AWS (EC2, Lambda, RDS, S3)")
        c.drawString(320, y_pos - 30, "• Docker/Kubernetes")
        c.drawString(320, y_pos - 45, "• Jenkins/GitHub Actions")
        c.drawString(320, y_pos - 60, "• Terraform/Ansible")
        
        # Start new page
        c.showPage()
        
        # Page 2: Experience section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 80, "PROFESSIONAL EXPERIENCE")
        c.line(100, height - 85, 500, height - 85)
        
        y_pos = height - 120
        
        # Job 1
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "Senior Full-Stack Developer")
        c.drawString(400, y_pos, "2020 - Present")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y_pos - 15, "TechCorp Inc. | San Francisco, CA")
        
        c.setFont("Helvetica", 10)
        achievements = [
            "• Led a team of 5 developers in building a microservices architecture using Python, Django, and React",
            "• Implemented CI/CD pipelines with Jenkins and Docker, reducing deployment time by 60%",
            "• Designed and developed RESTful APIs serving 100K+ daily requests with 99.9% uptime",
            "• Built machine learning models using TensorFlow for recommendation systems",
            "• Optimized PostgreSQL queries and database design, improving performance by 40%",
            "• Mentored junior developers and conducted code reviews"
        ]
        
        y_pos -= 35
        for achievement in achievements:
            c.drawString(120, y_pos, achievement)
            y_pos -= 15
        
        # Job 2
        y_pos -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "Full-Stack Developer")
        c.drawString(400, y_pos, "2018 - 2020")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(100, y_pos - 15, "StartupXYZ | Remote")
        
        c.setFont("Helvetica", 10)
        achievements2 = [
            "• Developed responsive web applications using React, Redux, and Node.js",
            "• Built and maintained Django REST APIs with PostgreSQL database",
            "• Implemented real-time features using WebSockets and Redis",
            "• Set up monitoring and logging with ELK stack",
            "• Collaborated with product and design teams in agile environment"
        ]
        
        y_pos -= 35
        for achievement in achievements2:
            c.drawString(120, y_pos, achievement)
            y_pos -= 15
        
        # Education
        y_pos -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_pos, "EDUCATION")
        c.line(100, y_pos - 5, 500, y_pos - 5)
        
        y_pos -= 25
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "Master of Science in Computer Science")
        c.drawString(400, y_pos, "2016 - 2018")
        c.setFont("Helvetica", 10)
        c.drawString(100, y_pos - 15, "Stanford University | GPA: 3.8/4.0")
        c.drawString(100, y_pos - 30, "Specialization: Machine Learning and Artificial Intelligence")
        
        y_pos -= 50
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y_pos, "Bachelor of Science in Software Engineering")
        c.drawString(400, y_pos, "2012 - 2016")
        c.setFont("Helvetica", 10)
        c.drawString(100, y_pos - 15, "University of California, Berkeley | GPA: 3.7/4.0")
        
        # Certifications
        y_pos -= 45
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_pos, "CERTIFICATIONS")
        c.line(100, y_pos - 5, 500, y_pos - 5)
        
        y_pos -= 25
        c.setFont("Helvetica", 10)
        certs = [
            "• AWS Certified Solutions Architect - Professional (2023)",
            "• Google Cloud Professional Cloud Architect (2022)",
            "• Certified Kubernetes Administrator (CKA) (2021)",
            "• MongoDB Certified Developer (2020)"
        ]
        
        for cert in certs:
            c.drawString(120, y_pos, cert)
            y_pos -= 15
        
        c.save()
        print(f"✅ Complex test PDF created successfully")
        
    except ImportError:
        print("❌ reportlab not available, cannot create test PDF")

def test_complex_pdf_processing():
    """Test complex PDF processing"""
    print("=" * 80)
    print("TESTING ENHANCED PDF PROCESSING WITH COMPLEX RESUME")
    print("=" * 80)
    
    # Create complex test PDF
    complex_pdf_path = project_root / "complex_test_resume.pdf"
    print(f"\n1. Creating complex test PDF at: {complex_pdf_path}")
    create_complex_test_pdf(complex_pdf_path)
    
    if complex_pdf_path.exists():
        print("\n2. Testing enhanced PDF extraction:")
        try:
            extracted_text = PDFProcessor.extract_text_from_pdf(str(complex_pdf_path))
            print(f"✅ PDF extraction successful!")
            print(f"   Extracted {len(extracted_text)} characters")
            print(f"   Word count: {len(extracted_text.split())} words")
            print("\n--- Extracted Text Preview ---")
            print(extracted_text[:1000] + "...")
            
            print("\n3. Testing enhanced AI analyzer:")
            analyzer = EnhancedAIAnalyzer()
            analysis_results = analyzer.analyze_resume(extracted_text)
            
            print(f"✅ Analysis completed!")
            print(f"   Experience level: {analysis_results.get('experience_level', 'N/A')}")
            print(f"   Years of experience: {analysis_results.get('years_of_experience', 0)}")
            print(f"   Skills found: {len(analysis_results.get('extracted_skills', []))}")
            print(f"   Programming languages: {analysis_results.get('programming_languages', [])}")
            print(f"   Frameworks: {analysis_results.get('frameworks_libraries', [])}")
            print(f"   Databases: {analysis_results.get('databases', [])}")
            print(f"   Cloud platforms: {analysis_results.get('cloud_platforms', [])}")
            print(f"   Confidence score: {analysis_results.get('confidence_score', 0)}")
            
            print("\n4. Full skill extraction results:")
            all_skills = analysis_results.get('extracted_skills', [])
            if all_skills:
                print(f"   Total skills extracted: {len(all_skills)}")
                for i, skill in enumerate(all_skills[:20], 1):  # Show first 20 skills
                    print(f"   {i:2d}. {skill}")
                if len(all_skills) > 20:
                    print(f"   ... and {len(all_skills) - 20} more skills")
            
        except Exception as e:
            print(f"❌ PDF processing failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Could not create complex test PDF")
    
    print("\n" + "=" * 80)
    print("COMPLEX PDF TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_complex_pdf_processing()
