#!/usr/bin/env python3
"""
Test script to verify encoding fixes work correctly
"""
import os
import sys
import django

# Add the Django project to Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_text_cleaning():
    """Test the text cleaning functionality"""
    import unicodedata
    import re
    
    def clean_text(text):
        """Clean and normalize text to prevent encoding issues"""
        if not text:
            return ""
        
        # First, handle any encoding issues
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # Remove or replace problematic characters
        # Keep alphanumeric, whitespace, and common punctuation
        cleaned = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\\@\#\$\%\^\&\*\+\=\|\~\`]', ' ', text)
        
        # Normalize unicode characters
        try:
            cleaned = unicodedata.normalize('NFKD', cleaned)
        except:
            pass
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Ensure it's valid UTF-8
        try:
            cleaned.encode('utf-8').decode('utf-8')
            return cleaned
        except UnicodeError:
            # More aggressive cleaning
            return ''.join(char for char in cleaned if ord(char) < 128)
    
    # Test cases with problematic characters
    test_strings = [
        "Normal text with no issues",
        "Text with unicode: café résumé naïve",
        "Text with byte 0x9c: \x9c problematic",
        "Mixed encoding: Hello\x00World\ufffd",
        "Binary data: \x80\x81\x82\x83",
        ""
    ]
    
    print("Testing text cleaning function:")
    print("=" * 50)
    
    for i, test_str in enumerate(test_strings, 1):
        try:
            cleaned = clean_text(test_str)
            print(f"Test {i}: SUCCESS")
            print(f"  Original: {repr(test_str)}")
            print(f"  Cleaned:  {repr(cleaned)}")
            
            # Verify it's valid JSON-safe
            import json
            json.dumps({"text": cleaned})
            print(f"  JSON-safe: YES")
            
        except Exception as e:
            print(f"Test {i}: FAILED - {e}")
        
        print()

def test_json_cleaning():
    """Test JSON cleaning functionality"""
    import json
    import unicodedata
    
    def clean_json_string(text):
        """Clean text to ensure it's safe for JSON parsing"""
        if not text:
            return text
        
        # Remove null bytes and replacement characters
        text = text.replace('\x00', '').replace('\ufffd', '')
        
        try:
            # Normalize unicode
            text = unicodedata.normalize('NFKD', text)
        except:
            pass
        
        # Remove problematic characters that can break JSON
        # Keep only valid JSON characters
        allowed_chars = set('{}[]":,\t\n\r abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_/@#$%^&*()+=|\\~`\'?!<>')
        cleaned = ''.join(char for char in text if char in allowed_chars or ord(char) < 256)
        
        # Ensure it's valid UTF-8
        try:
            cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            # Fallback to ASCII only
            cleaned = ''.join(char for char in cleaned if ord(char) < 128)
        
        return cleaned
    
    # Test JSON strings with problematic characters
    test_jsons = [
        '{"skills": ["Python", "JavaScript"], "experience": "senior"}',
        '{"skills": ["Python", "café"], "experience": "senior"}',  # Unicode
        '{"skills": ["Python\x9c", "JavaScript"], "experience": "senior"}',  # Problematic byte
        '{"text": "Hello\x00World\ufffd"}',  # Null bytes and replacement chars
    ]
    
    print("Testing JSON cleaning function:")
    print("=" * 50)
    
    for i, test_json in enumerate(test_jsons, 1):
        try:
            cleaned = clean_json_string(test_json)
            parsed = json.loads(cleaned)
            print(f"Test {i}: SUCCESS")
            print(f"  Original: {repr(test_json)}")
            print(f"  Cleaned:  {repr(cleaned)}")
            print(f"  Parsed:   {parsed}")
            
        except Exception as e:
            print(f"Test {i}: FAILED - {e}")
        
        print()

if __name__ == "__main__":
    print("Testing encoding fixes...")
    print("=" * 60)
    test_text_cleaning()
    print("=" * 60)
    test_json_cleaning()
    print("=" * 60)
    print("All tests completed!")
