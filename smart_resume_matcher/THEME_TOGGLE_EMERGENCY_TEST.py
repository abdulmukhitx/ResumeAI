#!/usr/bin/env python3
"""
EMERGENCY THEME TOGGLE VISIBILITY TEST
=====================================

This script tests that the theme toggle button is visible and functional
after our emergency visibility fixes.
"""

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Setup Chrome driver with specific options for testing"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"❌ Failed to setup Chrome driver: {e}")
        return None

def test_theme_toggle_visibility(driver, base_url):
    """Test that the theme toggle button is visible and functional"""
    print("🔍 Testing Theme Toggle Button Visibility...")
    
    try:
        # Navigate to home page
        driver.get(base_url)
        print(f"✅ Navigated to: {base_url}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check if theme toggle button exists
        theme_selectors = [
            '#theme-toggle',
            '.theme-toggle',
            'button.theme-toggle',
            'button[aria-label*="toggle"]',
            'button[aria-label*="theme"]'
        ]
        
        theme_button = None
        for selector in theme_selectors:
            try:
                theme_button = driver.find_element(By.CSS_SELECTOR, selector)
                if theme_button:
                    print(f"✅ Theme button found with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        if not theme_button:
            print("❌ CRITICAL: Theme toggle button not found with any selector!")
            return False
            
        # Check if button is visible
        is_displayed = theme_button.is_displayed()
        print(f"🔍 Button is_displayed(): {is_displayed}")
        
        # Check CSS properties
        button_styles = {
            'display': driver.execute_script("return window.getComputedStyle(arguments[0]).display", theme_button),
            'visibility': driver.execute_script("return window.getComputedStyle(arguments[0]).visibility", theme_button),
            'opacity': driver.execute_script("return window.getComputedStyle(arguments[0]).opacity", theme_button),
            'width': driver.execute_script("return window.getComputedStyle(arguments[0]).width", theme_button),
            'height': driver.execute_script("return window.getComputedStyle(arguments[0]).height", theme_button),
            'background': driver.execute_script("return window.getComputedStyle(arguments[0]).background", theme_button),
            'z-index': driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex", theme_button),
        }
        
        print("🎨 Button CSS Properties:")
        for prop, value in button_styles.items():
            print(f"   {prop}: {value}")
        
        # Check if button is clickable
        try:
            # Get current theme
            current_theme = driver.execute_script("return document.documentElement.getAttribute('data-theme')")
            print(f"🌙 Current theme: {current_theme}")
            
            # Click the button
            theme_button.click()
            print("✅ Theme button clicked successfully")
            
            # Wait a moment for theme to change
            time.sleep(1)
            
            # Check if theme changed
            new_theme = driver.execute_script("return document.documentElement.getAttribute('data-theme')")
            print(f"🌙 New theme: {new_theme}")
            
            if new_theme != current_theme:
                print("✅ Theme toggle is WORKING! Theme changed successfully.")
                return True
            else:
                print("❌ Theme toggle button clicked but theme did not change")
                return False
                
        except Exception as e:
            print(f"❌ Error clicking theme button: {e}")
            return False
            
    except TimeoutException:
        print("❌ Page load timeout")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_css_loading(driver, base_url):
    """Test that our emergency CSS file is being loaded"""
    print("📋 Testing CSS File Loading...")
    
    try:
        driver.get(base_url)
        
        # Check if our emergency CSS file is loaded
        css_links = driver.find_elements(By.CSS_SELECTOR, 'link[rel="stylesheet"]')
        
        emergency_css_loaded = False
        for link in css_links:
            href = link.get_attribute('href')
            if 'emergency-visibility-fix.css' in href:
                emergency_css_loaded = True
                print(f"✅ Emergency CSS file found: {href}")
                break
        
        if not emergency_css_loaded:
            print("❌ Emergency visibility fix CSS file not found!")
            return False
        
        # Test if our CSS rules are being applied
        theme_button = driver.find_element(By.CSS_SELECTOR, '.theme-toggle')
        if theme_button:
            z_index = driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex", theme_button)
            background = driver.execute_script("return window.getComputedStyle(arguments[0]).background", theme_button)
            
            # Our emergency CSS sets z-index to 99999
            if '99999' in str(z_index):
                print("✅ Emergency CSS rules are being applied (z-index: 99999)")
                return True
            else:
                print(f"❌ Emergency CSS not applied properly (z-index: {z_index})")
                return False
        
    except Exception as e:
        print(f"❌ Error testing CSS loading: {e}")
        return False

def main():
    """Main test function"""
    print("🚨 EMERGENCY THEME TOGGLE VISIBILITY TEST")
    print("=" * 50)
    
    # Test URL
    base_url = "http://localhost:8080"
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup browser driver")
        return False
    
    try:
        # Test CSS loading
        css_test = test_css_loading(driver, base_url)
        
        # Test theme toggle visibility and functionality
        visibility_test = test_theme_toggle_visibility(driver, base_url)
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY:")
        print(f"   CSS Loading: {'✅ PASS' if css_test else '❌ FAIL'}")
        print(f"   Theme Toggle: {'✅ PASS' if visibility_test else '❌ FAIL'}")
        
        if css_test and visibility_test:
            print("\n🎉 ALL TESTS PASSED! Theme toggle is visible and working!")
            return True
        else:
            print("\n❌ TESTS FAILED! Theme toggle needs additional fixes.")
            return False
            
    finally:
        driver.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
