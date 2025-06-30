#!/usr/bin/env python3
"""
Comprehensive Cleanup Script
============================

This script removes ALL unnecessary development, test, debug, and documentation files
that keep getting restored in the ResumeAI project.
"""

import os
import shutil
import glob

def cleanup_all_unnecessary_files():
    """Remove all unnecessary files and directories"""
    
    base_dir = "/home/abdulmukhit/Desktop/ResumeAI"
    django_dir = os.path.join(base_dir, "smart_resume_matcher")
    
    print("🧹 Starting comprehensive cleanup...")
    print("=" * 50)
    
    # Root level files to remove
    root_files_to_remove = [
        "DEPLOYMENT_STATUS.md",
        "DEPLOYMENT_STATUS_FINAL.md", 
        "DEPLOYMENT_SUMMARY.py",
        "TASK_COMPLETION_SUMMARY.md",
        "build.sh",
        "deploy_production.sh",
        "final_verification.py",
        "run_web.sh",
        "setup_sqlite_persistence.sh",
        "smart_resume_matcher.wsgi.py",
        "start.sh",
        "start_gunicorn.sh",
        "test_production.py",
        "wsgi.py"
    ]
    
    # Django app level files to remove (all test, debug, and documentation files)
    django_files_to_remove = [
        # Documentation and summary files
        "BEAUTIFUL_DARK_MODE_SUMMARY.md",
        "CLEAN_JWT_IMPLEMENTATION_SUMMARY.md", 
        "FINAL_MISSION_ACCOMPLISHED.md",
        "FINAL_SUCCESS_REPORT.md",
        "FINAL_VERIFICATION_REPORT.md",
        "INFINITE_REDIRECT_LOOP_COMPLETELY_FIXED.md",
        "INFINITE_REDIRECT_LOOP_FIX_SUCCESS.md",
        "JWT_AUTHENTICATION_COMPLETED.md",
        "JWT_AUTHENTICATION_TEST_GUIDE.md",
        "JWT_INFINITE_REDIRECT_FIXES_COMPLETE.md",
        "JWT_REDIRECT_FIX_SUCCESS_REPORT.md",
        "JWT_UI_FIXES_COMPLETED.md",
        "JWT_UPLOAD_PAGE_FIX_SUCCESS.md",
        "LOGIN_REDIRECT_FIX_COMPLETE.md",
        "MISSION_ACCOMPLISHED.md",
        "MISSION_ACCOMPLISHED_FINAL_REPORT.md",
        "THEME_SYSTEM_FIX_SUMMARY.md",
        "THEME_TOGGLE_VISIBILITY_FIX_SUCCESS.md",
        "ULTIMATE_SUCCESS_REPORT.md",
        
        # Test files
        "test_*.py",
        "test_*.html",
        "*_test.py",
        "*_test.html",
        
        # Debug files
        "debug_*.py",
        "debug_*.html",
        
        # Verification files
        "verify_*.py",
        "*_verification.py",
        "COMPLETE_JWT_REDIRECT_FIX_VERIFICATION.py",
        "FINAL_INFINITE_REDIRECT_FIX_VERIFICATION.py",
        "FINAL_JWT_VERIFICATION_COMPLETE.py",
        "FINAL_SUCCESS_VERIFICATION.py",
        
        # Console and JavaScript debug files
        "CONSOLE_DEBUG_COMMANDS.js",
        "IMMEDIATE_CONSOLE_FIX.js",
        
        # Report and summary scripts
        "javascript_fix_summary.py",
        "jwt_success_report.py", 
        "jwt_syntax_fix_summary.py",
        "ULTIMATE_SUCCESS_REPORT.py",
        "SIMPLE_THEME_TOGGLE_TEST.py",
        "THEME_TOGGLE_EMERGENCY_TEST.py",
        
        # Build and deployment files
        "build.sh",
        "final_deployment_summary.sh",
        "final_success_report.sh", 
        "final_success_verification.sh",
        "Procfile",
        "render.yaml",
        "requirements.txt",
        "setup_groq.sh",
        "setup_postgresql.sh",
        "setup_sqlite_persistence.sh",
        "start.sh",
        
        # Sync and deployment scripts
        "production_deployment_sync.py",
        "sync_production.py",
        "system_health_check.py",
        "start_and_test.py",
        
        # Migration and analysis files (keeping enhanced_resume_analysis.py)
        "analyze_resume.py",
        "migrate_to_postgresql.py",
        "extract_pdf.py",
        "check_database_health.py",
        "cleanup_users.py",
        
        # Demo and test data
        "live_demo.py",
        "mock_resume.txt",
        
        # HTML test files
        "dark_mode_test.html",
        "enhanced_dark_mode_test.html", 
        "infinite_redirect_fix_test.html",
        "jwt_ui_test.html",
        "redirect_test.html",
        "test_dark_mode_simple.html",
        "theme_toggle_test.html",
        "test_visibility.html",
        
        # Comprehensive test files
        "complete_login_test.py",
        "comprehensive_auth_test.py",
        "comprehensive_jwt_test.py",
        "emergency_redirect_fix_test.py",
        "final_clean_jwt_verification.py",
        "final_dark_mode_test.py",
        "final_deployment_verification.py", 
        "final_infinite_redirect_fix_verification.py",
        "final_integration_test.py",
        "final_jwt_fixes_test.py",
        "final_jwt_login_test.py",
        "final_jwt_verification.py",
        "final_login_redirect_test.py",
        "frontend_error_test.py",
        "manual_login_test.py"
    ]
    
    # Directories to remove completely
    dirs_to_remove = [
        os.path.join(base_dir, "docs"),
        os.path.join(django_dir, "docs"),
        os.path.join(django_dir, ".github")
    ]
    
    removed_count = 0
    
    # Remove root level files
    print("🗑️ Removing root level unnecessary files...")
    for filename in root_files_to_remove:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"   ✅ Removed: {filename}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {filename}: {e}")
    
    # Remove Django app level files using glob patterns
    print("\n🗑️ Removing Django app unnecessary files...")
    os.chdir(django_dir)
    
    for pattern in django_files_to_remove:
        matching_files = glob.glob(pattern)
        for filepath in matching_files:
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    print(f"   ✅ Removed: {filepath}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {filepath}: {e}")
    
    # Remove directories
    print("\n🗑️ Removing unnecessary directories...")
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Removed directory: {os.path.basename(dir_path)}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove directory {dir_path}: {e}")
    
    # Clean up __pycache__ directories
    print("\n🗑️ Cleaning __pycache__ directories...")
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"   ✅ Removed: {pycache_path}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {pycache_path}: {e}")
    
    # Clean up .pyc files
    print("\n🗑️ Cleaning .pyc files...")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"   ✅ Removed: {pyc_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Failed to remove {pyc_path}: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎉 Cleanup completed! Removed {removed_count} files/directories.")
    
    # Show what essential files remain
    print("\n📋 Essential files that remain:")
    essential_files = [
        "manage.py",
        "enhanced_resume_analysis.py", 
        ".env",
        ".env.example",
        ".gitignore",
        "README.md"
    ]
    
    for filename in essential_files:
        filepath = os.path.join(django_dir, filename)
        if os.path.exists(filepath):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ Missing: {filename}")
    
    return removed_count

if __name__ == "__main__":
    cleanup_all_unnecessary_files()
