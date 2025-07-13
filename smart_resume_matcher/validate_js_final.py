#!/usr/bin/env python3
"""
Final validation script to check JavaScript fixes in the job matches page.
"""

import re
import sys
import os

def validate_js_fixes():
    """Validate that JavaScript fixes have been applied correctly."""
    
    template_path = '/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher/templates/jobs/ai_job_matches.html'
    
    print("🔍 Validating JavaScript fixes in job matches page...")
    print(f"📁 Checking file: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"❌ File not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for duplicate variable declarations
    autoMatchBtn_matches = re.findall(r'const autoMatchBtn\s*=', content)
    if len(autoMatchBtn_matches) > 1:
        issues.append(f"❌ Found {len(autoMatchBtn_matches)} duplicate 'const autoMatchBtn' declarations")
    else:
        print("✅ No duplicate 'const autoMatchBtn' declarations found")
    
    searchForm_matches = re.findall(r'const searchForm\s*=', content)
    if len(searchForm_matches) > 1:
        issues.append(f"❌ Found {len(searchForm_matches)} duplicate 'const searchForm' declarations")
    else:
        print("✅ No duplicate 'const searchForm' declarations found")
    
    # Check for removed test functions
    test_functions = ['testAutoMatch', 'testAutoMatchSimple']
    for func in test_functions:
        if f'function {func}(' in content:
            issues.append(f"❌ Test function '{func}' should have been removed")
        else:
            print(f"✅ Test function '{func}' has been removed")
    
    # Check for onclick handlers referencing test functions
    onclick_patterns = [
        r'onclick="testAutoMatch.*?"',
        r'onclick="testAutoMatchSimple.*?"'
    ]
    
    for pattern in onclick_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"❌ Found onclick handler referencing test function: {matches}")
        else:
            print("✅ No onclick handlers referencing test functions found")
    
    # Check for extra closing braces
    js_section = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    if js_section:
        js_content = js_section.group(1)
        
        # Simple brace matching
        open_braces = js_content.count('{')
        close_braces = js_content.count('}')
        
        if open_braces != close_braces:
            issues.append(f"❌ Brace mismatch: {open_braces} open braces, {close_braces} close braces")
        else:
            print("✅ JavaScript brace matching looks correct")
    
    # Check for essential functions
    essential_functions = ['startAutoMatch', 'resetAutoMatchButton', 'updateJobsContainer']
    for func in essential_functions:
        if f'function {func}(' in content:
            print(f"✅ Essential function '{func}' is present")
        else:
            issues.append(f"❌ Essential function '{func}' is missing")
    
    # Check for proper event listener setup
    if 'addEventListener(\'click\', startAutoMatch)' in content:
        print("✅ Auto-match button event listener is properly set up")
    else:
        issues.append("❌ Auto-match button event listener is not properly set up")
    
    print("\n" + "="*50)
    
    if issues:
        print("❌ VALIDATION FAILED - Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ VALIDATION PASSED - All JavaScript fixes have been applied correctly!")
        print("\n📋 Summary of fixes applied:")
        print("  • Removed duplicate 'const autoMatchBtn' declarations")
        print("  • Removed duplicate 'const searchForm' declarations")
        print("  • Removed test functions (testAutoMatch, testAutoMatchSimple)")
        print("  • Removed onclick handlers referencing test functions")
        print("  • Fixed extra closing braces")
        print("  • Maintained essential functions and event listeners")
        return True

if __name__ == '__main__':
    success = validate_js_fixes()
    sys.exit(0 if success else 1)
