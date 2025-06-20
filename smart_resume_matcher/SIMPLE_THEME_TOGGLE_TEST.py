#!/usr/bin/env python3
"""
SIMPLE THEME TOGGLE VERIFICATION
================================

This script makes HTTP requests to test if our emergency CSS is being served
and if the theme toggle button HTML is present in the page.
"""

import requests
import re
from bs4 import BeautifulSoup

def test_emergency_css_served():
    """Test if the emergency CSS file is being served"""
    print("🔍 Testing Emergency CSS File...")
    
    try:
        # Test if emergency CSS file is accessible
        css_url = "http://localhost:8080/static/css/emergency-visibility-fix.css"
        response = requests.get(css_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Emergency CSS file is accessible")
            
            # Check if it contains our emergency fixes
            css_content = response.text
            if "theme-toggle" in css_content and "99999" in css_content:
                print("✅ Emergency CSS contains theme toggle fixes")
                return True
            else:
                print("❌ Emergency CSS doesn't contain expected fixes")
                return False
        else:
            print(f"❌ Emergency CSS file not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing emergency CSS: {e}")
        return False

def test_theme_toggle_html():
    """Test if theme toggle button is present in HTML"""
    print("🔍 Testing Theme Toggle Button HTML...")
    
    try:
        # Get home page
        response = requests.get("http://localhost:8080/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Home page accessible")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for theme toggle button
            theme_button = soup.find('button', {'id': 'theme-toggle'})
            if theme_button:
                print("✅ Theme toggle button found in HTML")
                print(f"   Button HTML: {theme_button}")
                
                # Check if emergency CSS is linked
                css_links = soup.find_all('link', {'rel': 'stylesheet'})
                emergency_css_found = False
                
                for link in css_links:
                    href = link.get('href', '')
                    if 'emergency-visibility-fix.css' in href:
                        emergency_css_found = True
                        print(f"✅ Emergency CSS linked: {href}")
                        break
                
                if emergency_css_found:
                    print("✅ Emergency CSS is properly linked in HTML")
                    return True
                else:
                    print("❌ Emergency CSS not found in HTML links")
                    return False
                    
            else:
                print("❌ Theme toggle button not found in HTML")
                # Let's search for any button with theme-related classes
                theme_buttons = soup.find_all('button', class_=re.compile(r'theme'))
                if theme_buttons:
                    print(f"   Found theme-related buttons: {theme_buttons}")
                else:
                    print("   No theme-related buttons found")
                return False
        else:
            print(f"❌ Home page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing HTML: {e}")
        return False

def test_javascript_files():
    """Test if main.js is being served and contains theme toggle code"""
    print("🔍 Testing JavaScript Files...")
    
    try:
        # Test main.js
        js_url = "http://localhost:8080/static/js/main.js"
        response = requests.get(js_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ main.js is accessible")
            
            js_content = response.text
            if "toggleTheme" in js_content and "theme-toggle" in js_content:
                print("✅ main.js contains theme toggle functionality")
                return True
            else:
                print("❌ main.js missing theme toggle functionality")
                return False
        else:
            print(f"❌ main.js not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing JavaScript: {e}")
        return False

def main():
    """Main test function"""
    print("🚨 SIMPLE THEME TOGGLE VERIFICATION")
    print("=" * 40)
    
    # Run tests
    css_test = test_emergency_css_served()
    html_test = test_theme_toggle_html()
    js_test = test_javascript_files()
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 TEST RESULTS:")
    print(f"   Emergency CSS: {'✅ PASS' if css_test else '❌ FAIL'}")
    print(f"   HTML Button: {'✅ PASS' if html_test else '❌ FAIL'}")
    print(f"   JavaScript: {'✅ PASS' if js_test else '❌ FAIL'}")
    
    if css_test and html_test and js_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("The theme toggle should now be visible and functional!")
        print("\n📋 Next steps:")
        print("1. Open http://localhost:8080 in your browser")
        print("2. Look for the purple theme toggle button in the navbar")
        print("3. Click it to test dark/light mode switching")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("The theme toggle may not be working properly.")
        return False

if __name__ == "__main__":
    main()
