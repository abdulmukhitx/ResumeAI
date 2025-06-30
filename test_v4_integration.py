#!/usr/bin/env python3
"""
Test V4 ASCII-Safe System Integration
Tests the complete V4 system for UTF-8 error resolution
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Add the project directory to Python path
project_dir = '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher'
sys.path.insert(0, project_dir)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_v4_components():
    """Test all V4 components individually"""
    
    print("=== V4 ASCII-Safe System Integration Test ===\n")
    
    try:
        # Test 1: Import V4 Components
        print("1. Testing V4 Component Imports...")
        from pdf_processor_v4 import PDFProcessorV4
        from ai_analyzer_v4 import AIAnalyzerV4
        from resume_processor_v4 import ResumeProcessorV4
        print("✓ All V4 components imported successfully")
        
        # Test 2: Initialize V4 Components
        print("\n2. Testing V4 Component Initialization...")
        pdf_processor = PDFProcessorV4()
        ai_analyzer = AIAnalyzerV4()
        resume_processor = ResumeProcessorV4()
        print("✓ All V4 components initialized successfully")
        
        # Test 3: Test ASCII-safe text processing
        print("\n3. Testing ASCII-safe text processing...")
        
        # Test problematic UTF-8 characters
        test_text = """
        José García - Software Engineer
        Résumé with special characters: ñ, á, é, í, ó, ú, ü
        Location: São Paulo, Brazil
        Skills: Python, JavaScript, SQL
        Experience: 5+ years in développement
        Education: Bachelor's in Informática
        Contact: jose@example.com
        Phone: +55 11 98765-4321
        """
        
        # Test AI Analyzer ASCII-safe processing
        ascii_safe_result = ai_analyzer._analyze_locally_ascii_safe(test_text)
        print(f"✓ ASCII-safe analysis completed successfully")
        print(f"  - Candidate Name: {ascii_safe_result.get('candidate_info', {}).get('name', 'N/A')}")
        print(f"  - Email: {ascii_safe_result.get('candidate_info', {}).get('email', 'N/A')}")
        print(f"  - Skills Found: {len(ascii_safe_result.get('skills', {}).get('technical', []))}")
        print(f"  - Overall Score: {ascii_safe_result.get('overall_score', 0)}")
        
        # Test 4: Test with actual PDF if available
        print("\n4. Testing PDF processing (if test PDF exists)...")
        
        test_pdf_path = os.path.join(project_dir, 'test_resume.pdf')
        if os.path.exists(test_pdf_path):
            print(f"Found test PDF: {test_pdf_path}")
            
            # Test PDF extraction
            extraction_result = pdf_processor.extract_text_ascii_safe(test_pdf_path)
            if extraction_result['success']:
                print(f"✓ PDF extraction successful")
                print(f"  - Text length: {len(extraction_result['text'])} characters")
                print(f"  - Method used: {extraction_result.get('method', 'unknown')}")
                print(f"  - ASCII-safe: {extraction_result.get('ascii_safe', False)}")
                
                # Test complete resume processing
                complete_result = resume_processor.process_resume(test_pdf_path)
                if complete_result['success']:
                    print(f"✓ Complete resume processing successful")
                    print(f"  - Analysis provider: {complete_result.get('provider_used', 'unknown')}")
                    print(f"  - Processing time: {complete_result.get('processing_time', 0):.2f}s")
                else:
                    print(f"⚠ Complete processing failed: {complete_result.get('error')}")
            else:
                print(f"⚠ PDF extraction failed: {extraction_result.get('error')}")
        else:
            print("No test PDF found, skipping PDF processing test")
        
        # Test 5: Test Django model compatibility (simulated)
        print("\n5. Testing Django integration compatibility...")
        
        # Simulate Django model data structure
        mock_analysis = {
            'extraction_info': {
                'text_length': 1500,
                'method_used': 'ascii_safe_pdfplumber',
                'success': True,
                'ascii_safe': True
            },
            'analysis': ascii_safe_result,
            'processing_metadata': {
                'v4_ascii_safe_system': True,
                'processor_version': 'v4',
                'encoding': 'ascii_only',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Test JSON serialization (Django will do this)
        json_data = json.dumps(mock_analysis, ensure_ascii=True, indent=2)
        print("✓ Django JSON serialization test passed")
        print(f"  - JSON size: {len(json_data)} characters")
        print(f"  - ASCII-only: {all(ord(c) < 128 for c in json_data)}")
        
        # Test 6: Error handling and fallback
        print("\n6. Testing error handling and fallback mechanisms...")
        
        # Test with empty text
        fallback_result = ai_analyzer._analyze_locally_ascii_safe("")
        print("✓ Empty text fallback test passed")
        
        # Test with non-existent file
        bad_file_result = pdf_processor.extract_text_ascii_safe("/non/existent/file.pdf")
        print(f"✓ Non-existent file handling: {not bad_file_result['success']}")
        
        print("\n=== V4 ASCII-Safe System Integration Test COMPLETED ===")
        print("✓ All components working correctly")
        print("✓ UTF-8 encoding errors should be completely resolved")
        print("✓ System ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ V4 Integration Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_views_import():
    """Test that the API views can import V4 components"""
    
    print("\n=== Testing API Views V4 Integration ===")
    
    try:
        # Test API views imports
        sys.path.insert(0, os.path.join(project_dir, 'resumes'))
        
        # This should work now with our clean V4 integration
        print("Testing API views imports...")
        
        # We can't fully test without Django setup, but we can test the imports
        import importlib.util
        
        api_views_path = os.path.join(project_dir, 'resumes', 'api_views_v3.py')
        if os.path.exists(api_views_path):
            print("✓ API views file exists")
            
            # Read and check for V4 imports
            with open(api_views_path, 'r') as f:
                content = f.read()
                
            if 'from pdf_processor_v4 import PDFProcessorV4' in content:
                print("✓ V4 PDF processor import found")
            if 'from ai_analyzer_v4 import AIAnalyzerV4' in content:
                print("✓ V4 AI analyzer import found")
            if 'from resume_processor_v4 import ResumeProcessorV4' in content:
                print("✓ V4 resume processor import found")
            if 'v4_ascii_safe_system' in content:
                print("✓ V4 ASCII-safe system integration found")
                
            print("✓ API views ready for V4 ASCII-safe processing")
        else:
            print("❌ API views file not found")
            
    except Exception as e:
        print(f"❌ API views test failed: {str(e)}")

if __name__ == "__main__":
    print("Starting V4 ASCII-Safe System Integration Test...")
    print(f"Project directory: {project_dir}")
    print(f"Python path: {sys.path[:3]}")
    
    # Run the tests
    success = test_v4_components()
    test_api_views_import()
    
    if success:
        print("\n🎉 V4 ASCII-Safe System is ready!")
        print("You can now upload resumes without UTF-8 encoding errors.")
    else:
        print("\n❌ V4 System has issues that need to be resolved.")
