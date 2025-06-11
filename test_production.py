#!/usr/bin/env python3
"""
Test production deployment of Smart Resume Matcher
"""
import requests
import json
import os
import time

# Production URL - update this with your actual Render URL
PRODUCTION_URL = "https://smart-resume-matcher.onrender.com"

def test_production_health():
    """Test if the production site is accessible"""
    print("🔍 Testing Production Deployment")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        print(f"Testing: {PRODUCTION_URL}")
        response = requests.get(PRODUCTION_URL, timeout=30)
        
        if response.status_code == 200:
            print("✅ Production site is accessible")
            print(f"Response time: {response.elapsed.total_seconds():.2f}s")
            
            # Check if it's actually the Django app
            if "Resume Matcher" in response.text or "django" in response.text.lower():
                print("✅ Django application is running")
            else:
                print("⚠️ Site accessible but may not be Django app")
                
        else:
            print(f"❌ Site returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to production site")
        print("This might be normal if the deployment is still in progress")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("Site might be starting up or overloaded")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_endpoints():
    """Test key API endpoints"""
    print("\n🔍 Testing API Endpoints")
    print("=" * 30)
    
    endpoints = [
        "/accounts/register/",
        "/accounts/login/", 
        "/resumes/upload/",
        "/api/jobs/",
    ]
    
    for endpoint in endpoints:
        try:
            url = PRODUCTION_URL + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code in [200, 403, 405]:  # These are expected
                print(f"✅ {endpoint} - Status: {response.status_code}")
            elif response.status_code == 404:
                print(f"⚠️ {endpoint} - Not found (404)")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def monitor_deployment_status():
    """Monitor deployment status by checking if site comes online"""
    print("\n🔍 Monitoring Deployment Status")
    print("=" * 35)
    
    max_attempts = 10
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            print(f"Attempt {attempt}/{max_attempts}...")
            response = requests.get(PRODUCTION_URL, timeout=15)
            
            if response.status_code == 200:
                print("✅ Deployment successful! Site is online.")
                return True
            else:
                print(f"Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("Site not yet accessible...")
        except Exception as e:
            print(f"Error: {e}")
            
        if attempt < max_attempts:
            print("Waiting 30 seconds before next check...")
            time.sleep(30)
        
        attempt += 1
    
    print("❌ Site did not come online within expected time")
    return False

if __name__ == "__main__":
    print("SMART RESUME MATCHER - PRODUCTION TEST")
    print("=" * 50)
    
    # First try immediate connection
    test_production_health()
    
    # If that fails, monitor for deployment completion
    print("\nIf the site is not accessible, it might still be deploying...")
    choice = input("Monitor deployment status? (y/n): ").lower().strip()
    
    if choice == 'y':
        if monitor_deployment_status():
            print("\n🎉 Running full test suite...")
            test_production_health()
            test_api_endpoints()
    else:
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("If there are issues, check the Render dashboard for deployment logs.")
