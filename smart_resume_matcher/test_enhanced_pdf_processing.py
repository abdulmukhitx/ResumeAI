#!/usr/bin/env python
"""
Test script for enhanced PDF processing functionality
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

def test_pdf_processor():
    """Test PDF processor with different scenarios"""
    print("=" * 60)
    print("TESTING ENHANCED PDF PROCESSING")
    print("=" * 60)
    
    # Test 1: Check if PDF processing libraries are available
    print("\n1. Testing PDF processing libraries availability:")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 is available")
    except ImportError:
        print("❌ PyPDF2 is NOT available")
    
    try:
        import pdfminer.six
        print("✅ pdfminer.six is available")
    except ImportError:
        print("❌ pdfminer.six is NOT available")
    
    try:
        import pdfplumber
        print("✅ pdfplumber is available")
    except ImportError:
        print("❌ pdfplumber is NOT available")
    
    try:
        import pytesseract
        import pdf2image
        print("✅ OCR libraries (pytesseract, pdf2image) are available")
    except ImportError:
        print("❌ OCR libraries are NOT available")
    
    # Test 2: Create a simple test PDF (if none exists)
    test_pdf_path = project_root / "test_resume.pdf"
    
    if not test_pdf_path.exists():
        print(f"\n2. Creating test PDF at: {test_pdf_path}")
        create_test_pdf(test_pdf_path)
    else:
        print(f"\n2. Using existing test PDF: {test_pdf_path}")
    
    # Test 3: Test PDF extraction
    if test_pdf_path.exists():
        print("\n3. Testing PDF text extraction:")
        try:
            extracted_text = PDFProcessor.extract_text_from_pdf(str(test_pdf_path))
            print(f"✅ PDF extraction successful!")
            print(f"   Extracted {len(extracted_text)} characters")
            print(f"   Preview: {extracted_text[:200]}...")
            
            # Test 4: Test enhanced analyzer
            print("\n4. Testing enhanced AI analyzer:")
            analyzer = EnhancedAIAnalyzer()
            analysis_results = analyzer.analyze_resume(extracted_text)
            
            print(f"✅ Analysis completed!")
            print(f"   Experience level: {analysis_results.get('experience_level', 'N/A')}")
            print(f"   Skills found: {len(analysis_results.get('extracted_skills', []))}")
            print(f"   Confidence score: {analysis_results.get('confidence_score', 0)}")
            
        except Exception as e:
            print(f"❌ PDF processing failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No test PDF available")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

def create_test_pdf(pdf_path):
    """Create a simple test PDF file"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Add test resume content
        c.drawString(100, 750, "John Doe")
        c.drawString(100, 730, "Software Engineer")
        c.drawString(100, 710, "Email: john.doe@example.com")
        c.drawString(100, 690, "Phone: (555) 123-4567")
        
        c.drawString(100, 650, "SKILLS:")
        c.drawString(120, 630, "• Python")
        c.drawString(120, 610, "• JavaScript")
        c.drawString(120, 590, "• React")
        c.drawString(120, 570, "• Django")
        c.drawString(120, 550, "• PostgreSQL")
        
        c.drawString(100, 510, "EXPERIENCE:")
        c.drawString(120, 490, "Senior Software Engineer at Tech Company (2020-2023)")
        c.drawString(120, 470, "• Developed web applications using Python and Django")
        c.drawString(120, 450, "• Built responsive frontends with React and JavaScript")
        c.drawString(120, 430, "• Managed PostgreSQL databases")
        
        c.save()
        print(f"✅ Test PDF created successfully")
        
    except ImportError:
        print("❌ reportlab not available, cannot create test PDF")
        print("   You can manually place a PDF file at the project root for testing")

if __name__ == "__main__":
    test_pdf_processor()
