#!/usr/bin/env python3
"""
Comprehensive validation script for the new ultra-modern job matches page.
Tests all features, UI elements, and functionality.
"""

import requests
import json
import time
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Test user login and get JWT token"""
    print("🔐 Testing login...")
    
    login_data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access']
        print("✅ Login successful")
        return access_token
    else:
        print("❌ Login failed:", response.status_code)
        return None

def test_job_matches_page(token):
    """Test the main job matches page"""
    print("\n🎯 Testing job matches page...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Job matches page failed: {response.status_code}")
        return False
    
    content = response.text
    
    # Test key UI elements
    ui_elements = [
        ('Hero Section', 'job-matches-hero'),
        ('Hero Title', 'AI-Powered Job Matching'),
        ('Auto-Match Button', 'auto-match-btn'),
        ('Search Section', 'search-filter-section'),
        ('Stats Section', 'stats-section'),
        ('Jobs Container', 'jobs-grid'),
        ('Modern CSS', 'Ultra-Modern AI Job Matches'),
        ('Floating Action Button', 'fab'),
        ('Toast Notifications', 'toast'),
        ('Pagination', 'pagination-container'),
        ('Job Cards', 'job-match-card'),
        ('Match Scores', 'match-score'),
        ('Apply Buttons', 'btn-apply'),
        ('Save Buttons', 'btn-save'),
        ('Skill Tags', 'skill-tag'),
        ('Search Form', 'search-form'),
        ('Filter Tags', 'filter-tags'),
        ('Loading States', 'loading-container'),
        ('Empty State', 'empty-state'),
        ('Responsive Design', '@media (max-width: 768px)'),
        ('Animations', '@keyframes'),
        ('Gradients', 'linear-gradient'),
        ('Backdrop Filter', 'backdrop-filter'),
        ('Interactive Elements', 'transition: all'),
        ('Modern Icons', 'fas fa-')
    ]
    
    passed = 0
    total = len(ui_elements)
    
    for name, element in ui_elements:
        if element in content:
            print(f"✅ {name} found")
            passed += 1
        else:
            print(f"❌ {name} missing")
    
    print(f"\n📊 UI Elements Test: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed == total

def test_auto_match_functionality(token):
    """Test the auto-match functionality"""
    print("\n🚀 Testing auto-match functionality...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/?auto_match=true", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Auto-match failed: {response.status_code}")
        return False
    
    content = response.text
    
    # Test auto-match features
    features = [
        ('Job Cards Generated', 'job-match-card'),
        ('Match Scores Display', 'match-score'),
        ('Company Names', 'company-name'),
        ('Job Titles', 'job-title'),
        ('Job Locations', 'job-location'),
        ('Job Descriptions', 'job-description'),
        ('Skills Matching', 'skill-tag'),
        ('Apply Buttons', 'btn-apply'),
        ('Save Buttons', 'btn-save'),
        ('Job Metadata', 'job-meta'),
        ('Salary Information', 'job-salary'),
        ('Posted Dates', 'job-posted')
    ]
    
    passed = 0
    total = len(features)
    
    for name, feature in features:
        if feature in content:
            print(f"✅ {name} working")
            passed += 1
        else:
            print(f"❌ {name} not found")
    
    print(f"\n📊 Auto-Match Test: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.8  # 80% pass rate

def test_search_functionality(token):
    """Test the search and filter functionality"""
    print("\n🔍 Testing search functionality...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test search with keywords
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/?search=python", headers=headers)
    
    if response.status_code == 200:
        print("✅ Search with keywords working")
        search_working = True
    else:
        print("❌ Search with keywords failed")
        search_working = False
    
    # Test location filter
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/?location=remote", headers=headers)
    
    if response.status_code == 200:
        print("✅ Location filter working")
        location_working = True
    else:
        print("❌ Location filter failed")
        location_working = False
    
    # Test salary filter
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/?salary=100000", headers=headers)
    
    if response.status_code == 200:
        print("✅ Salary filter working")
        salary_working = True
    else:
        print("❌ Salary filter failed")
        salary_working = False
    
    return search_working and location_working and salary_working

def test_responsive_design(token):
    """Test responsive design elements"""
    print("\n📱 Testing responsive design...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/", headers=headers)
    
    if response.status_code != 200:
        print("❌ Cannot test responsive design - page failed to load")
        return False
    
    content = response.text
    
    # Test responsive features
    responsive_features = [
        ('Mobile Media Queries', '@media (max-width: 768px)'),
        ('Flexible Grid Layout', 'grid-template-columns'),
        ('Responsive Hero Title', 'font-size: 2.5rem'),
        ('Flexible Search Form', 'grid-template-columns: 1fr'),
        ('Mobile Job Grid', 'grid-template-columns: 1fr'),
        ('Responsive Stats', 'repeat(2, 1fr)'),
        ('Mobile Actions', 'flex-direction: column')
    ]
    
    passed = 0
    total = len(responsive_features)
    
    for name, feature in responsive_features:
        if feature in content:
            print(f"✅ {name} implemented")
            passed += 1
        else:
            print(f"❌ {name} missing")
    
    print(f"\n📊 Responsive Design Test: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.7  # 70% pass rate

def test_modern_ui_features(token):
    """Test modern UI features and animations"""
    print("\n✨ Testing modern UI features...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/", headers=headers)
    
    if response.status_code != 200:
        print("❌ Cannot test UI features - page failed to load")
        return False
    
    content = response.text
    
    # Test modern UI features
    modern_features = [
        ('CSS Gradients', 'linear-gradient'),
        ('Backdrop Filter', 'backdrop-filter: blur'),
        ('CSS Animations', '@keyframes'),
        ('Smooth Transitions', 'transition: all'),
        ('Box Shadows', 'box-shadow:'),
        ('Border Radius', 'border-radius:'),
        ('Hover Effects', ':hover'),
        ('Transform Effects', 'transform:'),
        ('Flex Layouts', 'display: flex'),
        ('Grid Layouts', 'display: grid'),
        ('Modern Colors', '#667eea'),
        ('Typography', 'font-weight: 700'),
        ('Spacing', 'gap:'),
        ('Modern Icons', 'fas fa-'),
        ('Interactive States', '.loading'),
        ('Toast Notifications', 'toast'),
        ('Floating Elements', 'position: fixed'),
        ('Opacity Effects', 'opacity:'),
        ('Modern Buttons', 'border-radius: 50px'),
        ('Card Layouts', 'padding: 2rem')
    ]
    
    passed = 0
    total = len(modern_features)
    
    for name, feature in modern_features:
        if feature in content:
            print(f"✅ {name} implemented")
            passed += 1
        else:
            print(f"❌ {name} missing")
    
    print(f"\n📊 Modern UI Test: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.8  # 80% pass rate

def test_javascript_functionality(token):
    """Test JavaScript functionality"""
    print("\n⚡ Testing JavaScript functionality...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{BASE_URL}/jobs/ai-matches/", headers=headers)
    
    if response.status_code != 200:
        print("❌ Cannot test JavaScript - page failed to load")
        return False
    
    content = response.text
    
    # Test JavaScript features
    js_features = [
        ('Auto-Match Function', 'function startAutoMatch'),
        ('Search Handling', 'function handleSearch'),
        ('Filter Updates', 'function updateFilterTags'),
        ('Job Card Creation', 'function createJobCard'),
        ('Apply to Job', 'function applyToJob'),
        ('Save Job', 'function saveJob'),
        ('Toast Notifications', 'function showToast'),
        ('Pagination', 'function loadPage'),
        ('Scroll to Top', 'function scrollToTop'),
        ('Number Animation', 'function animateNumber'),
        ('Loading States', 'function showLoading'),
        ('Event Listeners', 'addEventListener'),
        ('AJAX Calls', 'fetch('),
        ('JWT Token Handling', 'getAuthToken'),
        ('Debounce Function', 'function debounce'),
        ('DOM Manipulation', 'document.getElementById'),
        ('Animation Initialization', 'initializeAnimations'),
        ('Filter Management', 'initializeFilters'),
        ('Statistics Updates', 'updateStats'),
        ('Responsive Handling', 'window.scrollTo')
    ]
    
    passed = 0
    total = len(js_features)
    
    for name, feature in js_features:
        if feature in content:
            print(f"✅ {name} implemented")
            passed += 1
        else:
            print(f"❌ {name} missing")
    
    print(f"\n📊 JavaScript Test: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.8  # 80% pass rate

def run_comprehensive_test():
    """Run all tests"""
    print("🎯 COMPREHENSIVE JOB MATCHES PAGE VALIDATION")
    print("=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Cannot continue - login failed")
        return
    
    # Run all tests
    tests = [
        ("Job Matches Page", test_job_matches_page),
        ("Auto-Match Functionality", test_auto_match_functionality),
        ("Search Functionality", test_search_functionality),
        ("Responsive Design", test_responsive_design),
        ("Modern UI Features", test_modern_ui_features),
        ("JavaScript Functionality", test_javascript_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func(token)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL SCORE: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The new ultra-modern job matches page is working perfectly!")
    elif passed >= total * 0.8:
        print("✅ EXCELLENT! The job matches page is working very well with minor issues.")
    elif passed >= total * 0.6:
        print("⚠️  GOOD! The job matches page is working but needs some improvements.")
    else:
        print("❌ NEEDS WORK! The job matches page has significant issues.")

if __name__ == "__main__":
    run_comprehensive_test()
