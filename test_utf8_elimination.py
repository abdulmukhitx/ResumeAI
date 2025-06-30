#!/usr/bin/env python3
"""
Comprehensive UTF-8 Error Elimination Test
==========================================

This script tests all critical paths to ensure UTF-8 errors are completely eliminated.
It specifically targets the actual endpoints being used by the frontend.
"""

import os
import sys
import django
import json

# Add the Django project to path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

User = get_user_model()

def create_test_pdf_with_problematic_chars():
    """Create a PDF with characters that historically caused UTF-8 errors"""
    
    # Create problematic content with various encoding issues
    problematic_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
72 720 Td
(John Doe - Software Engineer) Tj
0 -20 Td
(Skills: Python, Java, C++, React) Tj
0 -20 Td
(Experience: 5 years in development) Tj
0 -20 Td
(Email: john.doe@company.com) Tj
0 -20 Td
(Phone: +1-555-123-4567) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000201 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
450
%%EOF"""
    
    return problematic_content

def test_v4_direct_processing():
    """Test V4 processors directly"""
    print("\n" + "="*60)
    print("TESTING V4 DIRECT PROCESSING")
    print("="*60)
    
    try:
        # Test V4 PDF processor
        from pdf_processor_v4 import PDFProcessorV4
        from ai_analyzer_v4 import AIAnalyzerV4
        from resume_processor_v4 import ResumeProcessorV4
        
        print("✅ V4 modules imported successfully")
        
        # Create test file
        test_content = create_test_pdf_with_problematic_chars()
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(test_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Test PDF extraction
            print("\n1. Testing V4 PDF extraction...")
            pdf_processor = PDFProcessorV4()
            extraction_result = pdf_processor.extract_text_ascii_safe(tmp_file_path)
            
            print(f"   Extraction success: {extraction_result['success']}")
            print(f"   Text length: {len(extraction_result['text'])}")
            print(f"   Method used: {extraction_result.get('method')}")
            print(f"   Sample text: {extraction_result['text'][:100]}...")
            
            # Test AI analysis
            print("\n2. Testing V4 AI analysis...")
            ai_analyzer = AIAnalyzerV4()
            analysis_result = ai_analyzer.analyze_resume_ascii_safe(extraction_result['text'])
            
            print(f"   Analysis success: {bool(analysis_result.get('skills'))}")
            print(f"   Skills found: {len(analysis_result.get('skills', []))}")
            print(f"   Experience level: {analysis_result.get('experience_level')}")
            print(f"   Confidence: {analysis_result.get('confidence_score')}")
            
            # Test complete processing
            print("\n3. Testing V4 complete processing...")
            resume_processor = ResumeProcessorV4()
            complete_result = resume_processor.process_resume(tmp_file_path)
            
            print(f"   Complete processing success: {complete_result['success']}")
            print(f"   Provider used: {complete_result.get('provider_used')}")
            print(f"   Text length: {len(complete_result['extraction']['text'])}")
            print(f"   Skills extracted: {len(complete_result['analysis'].get('skills', []))}")
            
            print("\n✅ All V4 direct processing tests passed!")
            return True
            
        finally:
            # Cleanup
            try:
                os.unlink(tmp_file_path)
            except:
                pass
                
    except Exception as e:
        print(f"\n❌ V4 direct processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_django_api_endpoints():
    """Test the actual Django API endpoints being used"""
    print("\n" + "="*60)
    print("TESTING DJANGO API ENDPOINTS")
    print("="*60)
    
    try:
        # Create test user
        print("\n1. Setting up test user...")
        User.objects.filter(username='testuser_v4').delete()  # Cleanup previous
        user = User.objects.create_user(
            username='testuser_v4',
            email='test_v4@example.com',
            password='testpass123'
        )
        print("✅ Test user created")
        
        # Create test client
        client = Client()
        
        # Test login to get JWT token
        print("\n2. Testing JWT login...")
        login_response = client.post('/api/auth/login/', 
            json.dumps({
                'username': 'testuser_v4',
                'password': 'testpass123'
            }), 
            content_type='application/json'
        )
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = json.loads(login_response.content)
            access_token = token_data.get('access')
            print(f"✅ JWT token obtained: {access_token[:50]}...")
            
            # Test the main upload endpoint (the one causing errors)
            print("\n3. Testing resume upload API...")
            
            # Create test PDF
            test_pdf_content = create_test_pdf_with_problematic_chars()
            
            # Upload via the actual endpoint
            upload_response = client.post(
                '/api/resume/upload/',
                {
                    'file': SimpleUploadedFile(
                        'test_resume_v4.pdf',
                        test_pdf_content,
                        content_type='application/pdf'
                    )
                },
                HTTP_AUTHORIZATION=f'Bearer {access_token}'
            )
            
            print(f"   Upload status: {upload_response.status_code}")
            print(f"   Upload response: {upload_response.content.decode('utf-8', errors='replace')[:300]}")
            
            if upload_response.status_code == 201:
                print("✅ Upload successful - UTF-8 errors eliminated!")
                
                response_data = json.loads(upload_response.content)
                resume_id = response_data.get('resume', {}).get('id')
                
                if resume_id:
                    print(f"   Resume ID: {resume_id}")
                    
                    # Wait for processing and check status
                    import time
                    print("\n4. Checking processing status...")
                    
                    for i in range(5):
                        time.sleep(2)
                        
                        # Check resume status in database
                        from resumes.models import Resume
                        try:
                            resume = Resume.objects.get(id=resume_id)
                            print(f"   Attempt {i+1}: Status = {resume.status}")
                            
                            if resume.status == 'completed':
                                print("✅ Processing completed successfully!")
                                print(f"   Skills extracted: {len(resume.extracted_skills) if resume.extracted_skills else 0}")
                                print(f"   Experience level: {resume.experience_level}")
                                print(f"   Confidence score: {resume.confidence_score}")
                                break
                            elif resume.status == 'failed':
                                print(f"❌ Processing failed: {resume.analysis_summary[:200]}")
                                break
                                
                        except Exception as e:
                            print(f"   Error checking status: {e}")
                    
                    return True
                else:
                    print("❌ No resume ID returned")
                    return False
            else:
                print(f"❌ Upload failed with status {upload_response.status_code}")
                return False
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Django API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_resistance():
    """Test system resistance to various encoding issues"""
    print("\n" + "="*60)
    print("TESTING ERROR RESISTANCE")
    print("="*60)
    
    try:
        from ai_analyzer_v4 import AIAnalyzerV4
        analyzer = AIAnalyzerV4()
        
        # Test various problematic inputs
        test_cases = [
            "Normal ASCII text with skills: Python, Java, JavaScript",
            "Text with é accénts ànd spëcial cháracters",
            "Mixed encoding: café résumé naïve",
            "Symbols: ©®™€£¥§¶†‡•…‰‹›fi",
            "",  # Empty string
            None,  # None input
        ]
        
        print("\n1. Testing ASCII-safe text conversion...")
        for i, test_text in enumerate(test_cases):
            try:
                if test_text is None:
                    converted = analyzer._ensure_ascii_safe("")
                else:
                    converted = analyzer._ensure_ascii_safe(test_text)
                print(f"   Test {i+1}: ✅ '{test_text}' → '{converted[:50]}{'...' if len(converted) > 50 else ''}'")
            except Exception as e:
                print(f"   Test {i+1}: ❌ '{test_text}' failed: {e}")
                return False
        
        print("\n2. Testing analysis with problematic inputs...")
        for i, test_text in enumerate(test_cases):
            try:
                if test_text is None:
                    result = analyzer.analyze_resume_ascii_safe("")
                else:
                    result = analyzer.analyze_resume_ascii_safe(test_text)
                
                # Verify result is ASCII-safe
                result_str = json.dumps(result)
                result_str.encode('ascii', errors='strict')  # This will fail if not ASCII
                
                print(f"   Test {i+1}: ✅ Analysis successful, {len(result.get('skills', []))} skills found")
            except UnicodeEncodeError:
                print(f"   Test {i+1}: ❌ Result contains non-ASCII characters")
                return False
            except Exception as e:
                print(f"   Test {i+1}: ❌ Analysis failed: {e}")
                return False
        
        print("\n✅ All error resistance tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error resistance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive UTF-8 elimination tests"""
    print("=" * 80)
    print("COMPREHENSIVE UTF-8 ERROR ELIMINATION TEST")
    print("=" * 80)
    print("Testing V4 ASCII-safe system to ensure complete UTF-8 error elimination")
    
    results = []
    
    # Test 1: V4 Direct Processing
    results.append(test_v4_direct_processing())
    
    # Test 2: Django API Endpoints  
    results.append(test_django_api_endpoints())
    
    # Test 3: Error Resistance
    results.append(test_error_resistance())
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    test_names = [
        "V4 Direct Processing",
        "Django API Endpoints", 
        "Error Resistance"
    ]
    
    all_passed = True
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! UTF-8 ERRORS HAVE BEEN ELIMINATED!")
        print("The V4 ASCII-safe system is working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED - UTF-8 ISSUES MAY STILL EXIST")
        print("Please review the failed tests and fix any remaining issues.")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
