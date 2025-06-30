#!/usr/bin/env python3
"""
Direct test of the analysis pipeline to isolate the JSON error
"""
import os
import sys
import django

# Add the Django project to Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_current_resume_analysis():
    """Test analysis of existing resumes to find the problematic one"""
    from resumes.models import Resume
    from enhanced_resume_analysis import analyze_resume
    import logging
    
    # Set up detailed logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    
    # Get the most recent resumes
    recent_resumes = Resume.objects.all().order_by('-created_at')[:5]
    
    print("Testing analysis of recent resumes:")
    print("=" * 50)
    
    for resume in recent_resumes:
        print(f"\nTesting Resume ID: {resume.id}")
        print(f"Filename: {resume.original_filename}")
        print(f"Size: {resume.file_size} bytes")
        print(f"Current Status: {resume.status}")
        
        try:
            # Try to analyze this resume
            print("Starting analysis...")
            result = analyze_resume(resume.id)
            print(f"✅ Analysis result: {result}")
            
            # Check the updated status
            resume.refresh_from_db()
            print(f"Final status: {resume.status}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        print("-" * 30)

def test_problematic_text():
    """Test with text that contains the problematic byte"""
    print("\nTesting problematic text handling:")
    print("=" * 50)
    
    # Create text with the problematic byte 0x9c
    problematic_text = "This is a test resume with problematic byte: \x9c and some other content."
    
    try:
        from enhanced_resume_analysis import AIAnalyzer
        analyzer = AIAnalyzer()
        
        print("Testing with problematic text...")
        result = analyzer.analyze_resume(problematic_text)
        print(f"✅ Analysis successful: {result}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_current_resume_analysis()
    test_problematic_text()
