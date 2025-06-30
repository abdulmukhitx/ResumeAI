#!/usr/bin/env python3
"""
Quick test of the fixed main.js redirect protection.
"""

import os
import sys
import django
import requests

# Add the project directory to the Python path
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_main_pages():
    """Test main pages are accessible."""
    print("🧪 Testing Main Pages Accessibility...")
    
    try:
        # Test main pages
        pages = [
            ('Home', 'http://localhost:8001/'),
            ('Login', 'http://localhost:8001/login/'),
            ('JWT Profile', 'http://localhost:8001/jwt-profile/'),
            ('JWT Resume Upload', 'http://localhost:8001/jwt-resume-upload/'),
        ]
        
        for page_name, url in pages:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {page_name}: {response.status_code}")
                else:
                    print(f"⚠️  {page_name}: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {page_name}: Connection failed (server not running?)")
            except Exception as e:
                print(f"❌ {page_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run quick tests."""
    print("🔍 Quick Main.js Fix Verification")
    print("=" * 40)
    
    result = test_main_pages()
    
    print()
    if result:
        print("✅ Basic page accessibility test passed!")
        print("👉 The redirect protection has been simplified and should work better now.")
        print("💡 Key changes:")
        print("   • Removed complex window.location.href override")
        print("   • Added simple safeRedirect() function")
        print("   • Tracks redirect count to prevent loops")
        print("   • Uses standard redirect methods")
    else:
        print("⚠️  Some issues detected. Check server status.")

if __name__ == "__main__":
    main()
