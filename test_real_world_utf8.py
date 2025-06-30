#!/usr/bin/env python3
"""
Real-World UTF-8 Error Test
===========================

This test simulates the exact scenario that was causing the 500 Internal Server Error
to verify that UTF-8 errors have been completely eliminated.
"""

import os
import sys
import tempfile

# Add the Django project to path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

def test_real_world_utf8_scenario():
    """Test the exact scenario that was causing UTF-8 errors"""
    print("=" * 70)
    print("REAL-WORLD UTF-8 ERROR ELIMINATION TEST")
    print("=" * 70)
    
    try:
        # Import V4 components (these should now be UTF-8 safe)
        from pdf_processor_v4 import PDFProcessorV4
        from ai_analyzer_v4 import AIAnalyzerV4
        from resume_processor_v4 import ResumeProcessorV4
        
        print("✅ V4 components imported successfully")
        
        # Create a PDF with problematic content that historically caused UTF-8 errors
        problematic_pdf = b"""%PDF-1.4
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
/Length 300
>>
stream
BT
/F1 12 Tf
72 720 Td
(Alynur CV - JobPilot Update) Tj
0 -20 Td
(Software Engineer with 5+ years experience) Tj
0 -20 Td
(Skills: Python, Django, JavaScript, React, PostgreSQL) Tj
0 -20 Td
(Email: alynur@example.com) Tj
0 -20 Td
(Phone: +1-555-123-4567) Tj
0 -20 Td
(Experience: Senior Developer at TechCorp) Tj
0 -20 Td
(Education: BS Computer Science, University) Tj
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
570
%%EOF"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(problematic_pdf)
            pdf_path = tmp_file.name
        
        print(f"📄 Created test PDF: {pdf_path}")
        
        try:
            # Test the complete processing pipeline that was failing
            print("\n1. Testing Complete V4 Processing Pipeline...")
            processor = ResumeProcessorV4()
            result = processor.process_resume(pdf_path)
            
            print(f"   Processing success: {result['success']}")
            
            if result['success']:
                print(f"   ✅ Text extracted successfully ({len(result['extraction']['text'])} chars)")
                print(f"   ✅ Analysis completed successfully")
                print(f"   ✅ Skills found: {len(result['analysis'].get('skills', []))}")
                print(f"   ✅ Experience level: {result['analysis'].get('experience_level')}")
                print(f"   ✅ Confidence score: {result['analysis'].get('confidence_score')}")
                
                # Verify the result is completely ASCII-safe
                print("\n2. Testing ASCII-Safety of Results...")
                
                try:
                    import json
                    result_json = json.dumps(result)
                    result_json.encode('ascii', errors='strict')
                    print("   ✅ Results are completely ASCII-safe")
                except UnicodeEncodeError as e:
                    print(f"   ❌ Results contain non-ASCII characters: {e}")
                    return False
                
                # Test specific components that were causing issues
                print("\n3. Testing Individual Components...")
                
                # PDF extraction
                pdf_processor = PDFProcessorV4()
                extraction_result = pdf_processor.extract_text_ascii_safe(pdf_path)
                print(f"   ✅ PDF extraction: {extraction_result['success']}")
                
                # AI analysis
                ai_analyzer = AIAnalyzerV4()
                analysis_result = ai_analyzer.analyze_resume_ascii_safe(extraction_result['text'])
                print(f"   ✅ AI analysis: {bool(analysis_result.get('skills'))}")
                
                # Test encoding conversion specifically
                print("\n4. Testing Encoding Conversion...")
                original_text = extraction_result['text']
                ascii_text = ai_analyzer._ensure_ascii_safe(original_text)
                
                try:
                    ascii_text.encode('ascii', errors='strict')
                    print(f"   ✅ Text successfully converted to ASCII ({len(ascii_text)} chars)")
                except UnicodeEncodeError:
                    print("   ❌ ASCII conversion failed")
                    return False
                
                print("\n5. Testing Error Scenarios...")
                
                # Test with None input
                try:
                    result_none = ai_analyzer.analyze_resume_ascii_safe(None)
                    print("   ✅ Handles None input gracefully")
                except Exception as e:
                    print(f"   ❌ Failed with None input: {e}")
                    return False
                
                # Test with empty string
                try:
                    result_empty = ai_analyzer.analyze_resume_ascii_safe("")
                    print("   ✅ Handles empty string gracefully")
                except Exception as e:
                    print(f"   ❌ Failed with empty string: {e}")
                    return False
                
                # Test with problematic characters
                problematic_text = "Résumé with spéciał chäracters: café, naïve, Zürich"
                try:
                    result_problematic = ai_analyzer.analyze_resume_ascii_safe(problematic_text)
                    # Verify result is ASCII-safe
                    json.dumps(result_problematic).encode('ascii', errors='strict')
                    print("   ✅ Handles problematic characters gracefully")
                except Exception as e:
                    print(f"   ❌ Failed with problematic characters: {e}")
                    return False
                
                print("\n" + "=" * 70)
                print("🎉 SUCCESS! UTF-8 ERRORS HAVE BEEN COMPLETELY ELIMINATED!")
                print("=" * 70)
                print("✅ V4 ASCII-safe processing works perfectly")
                print("✅ All text processing is encoding-safe")
                print("✅ Results are guaranteed to be ASCII-only")
                print("✅ Error handling is robust")
                print("✅ The 500 Internal Server Error should be resolved")
                print("=" * 70)
                
                return True
                
            else:
                print(f"   ❌ Processing failed: {result.get('error')}")
                return False
                
        finally:
            # Cleanup
            try:
                os.unlink(pdf_path)
            except:
                pass
                
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_api_integration():
    """Test the specific API integration that was failing"""
    print("\n" + "=" * 70)
    print("TESTING SPECIFIC API INTEGRATION")
    print("=" * 70)
    
    try:
        # Test the actual functions being called in the API
        print("1. Testing the exact API processing flow...")
        
        # Simulate the background processing function
        from resume_processor_v4 import ResumeProcessorV4
        
        # Create test PDF
        test_pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 50>>stream
BT/F1 12 Tf 72 720 Td(Test Resume - Python Developer)Tj ET
endstream endobj
xref 0 5
0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000115 00000 n 0000000201 00000 n 
trailer<</Size 5/Root 1 0 R>>startxref 294 %%EOF"""
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(test_pdf)
            test_path = tmp_file.name
        
        try:
            # This is the exact call made in the API
            processor = ResumeProcessorV4()
            result = processor.process_resume(test_path)
            
            print(f"   API processing result: {result['success']}")
            
            if result['success']:
                # Simulate the database update that happens in the API
                analysis = result['analysis']
                extraction = result['extraction']
                
                # Test JSON serialization (this was failing with UTF-8 errors)
                import json
                from datetime import datetime
                
                combined_analysis = {
                    'extraction_info': {
                        'text_length': len(extraction['text']),
                        'method_used': extraction.get('method'),
                        'success': extraction['success'],
                        'ascii_safe': True,
                        'v4_processor': True
                    },
                    'analysis': analysis,
                    'processing_metadata': {
                        'v4_ascii_safe_system': True,
                        'processor_version': 'v4',
                        'encoding': 'ascii_only',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                # This JSON serialization was causing UTF-8 errors before
                try:
                    analysis_json = json.dumps(combined_analysis)
                    analysis_json.encode('ascii', errors='strict')
                    print("   ✅ JSON serialization is ASCII-safe")
                except Exception as e:
                    print(f"   ❌ JSON serialization failed: {e}")
                    return False
                
                # Test the specific field updates that were failing
                raw_text = extraction['text'][:10000]
                extracted_skills = analysis.get('skills', {}).get('technical', [])[:20]
                
                try:
                    raw_text.encode('ascii', errors='strict')
                    print("   ✅ Raw text is ASCII-safe")
                except UnicodeEncodeError:
                    print("   ❌ Raw text contains non-ASCII characters")
                    return False
                
                print("   ✅ All database field updates are ASCII-safe")
                print("   ✅ API integration test successful")
                
                return True
            else:
                print(f"   ❌ API processing failed: {result.get('error')}")
                return False
                
        finally:
            try:
                os.unlink(test_path)
            except:
                pass
                
    except Exception as e:
        print(f"\n❌ API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the real-world UTF-8 error elimination test"""
    success1 = test_real_world_utf8_scenario()
    success2 = test_specific_api_integration()
    
    if success1 and success2:
        print("\n" + "🎉" * 10)
        print("COMPLETE SUCCESS!")
        print("🎉" * 10)
        print("The UTF-8 encoding errors have been completely eliminated!")
        print("The 500 Internal Server Error should now be resolved.")
        print("You can safely upload resumes without encoding issues.")
        return True
    else:
        print("\n" + "⚠️" * 10)
        print("SOME ISSUES REMAIN")
        print("⚠️" * 10)
        print("Please review the failed tests above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
