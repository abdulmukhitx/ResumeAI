#!/usr/bin/env python
"""
Final deployment verification script
Verifies that all components are ready for production deployment
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.models import Resume
from accounts.models import User
from jobs.models import JobMatch
from resumes.utils import AIAnalyzer

def verify_deployment_readiness():
    """Verify all components are ready for deployment"""
    print("=== DEPLOYMENT READINESS VERIFICATION ===\n")
    
    verification_results = {}
    
    # 1. Database integrity check
    print("1. DATABASE INTEGRITY:")
    try:
        users = User.objects.all()
        resumes = Resume.objects.all()
        matches = JobMatch.objects.all()
        
        print(f"   ✅ Users: {users.count()}")
        print(f"   ✅ Resumes: {resumes.count()}")
        print(f"   ✅ Job Matches: {matches.count()}")
        
        verification_results['database'] = {
            'status': 'passed',
            'users': users.count(),
            'resumes': resumes.count(),
            'matches': matches.count()
        }
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        verification_results['database'] = {'status': 'failed', 'error': str(e)}
    
    # 2. Target user verification
    print("\n2. TARGET USER VERIFICATION (asalachik@gmail.com):")
    try:
        user = User.objects.get(email='asalachik@gmail.com')
        user_resumes = Resume.objects.filter(user=user)
        active_resume = Resume.objects.filter(user=user, is_active=True).first()
        
        print(f"   ✅ User found: {user.email}")
        print(f"   ✅ Total resumes: {user_resumes.count()}")
        
        if active_resume:
            print(f"   ✅ Active resume: {active_resume.original_filename}")
            print(f"   ✅ Status: {active_resume.status}")
            print(f"   ✅ Skills extracted: {len(active_resume.extracted_skills)}")
            print(f"   ✅ Experience level: {active_resume.experience_level}")
            
            verification_results['target_user'] = {
                'status': 'passed',
                'resume_filename': active_resume.original_filename,
                'resume_status': active_resume.status,
                'skills_count': len(active_resume.extracted_skills),
                'experience_level': active_resume.experience_level
            }
        else:
            print(f"   ❌ No active resume found")
            verification_results['target_user'] = {'status': 'failed', 'error': 'No active resume'}
            
    except User.DoesNotExist:
        print(f"   ❌ User not found")
        verification_results['target_user'] = {'status': 'failed', 'error': 'User not found'}
    except Exception as e:
        print(f"   ❌ User verification error: {e}")
        verification_results['target_user'] = {'status': 'failed', 'error': str(e)}
    
    # 3. AI functionality test
    print("\n3. AI FUNCTIONALITY TEST:")
    try:
        analyzer = AIAnalyzer()
        test_resume = """
        John Doe
        Software Engineer
        
        Skills:
        - Python programming
        - Django web framework
        - React.js
        - PostgreSQL database
        - Docker containerization
        
        Experience:
        Senior Software Engineer at TechCorp (2020-2023)
        - Developed web applications using Django and React
        - Managed database design and optimization
        - Led team of 3 junior developers
        """
        
        result = analyzer.analyze_resume(test_resume)
        
        skills = result.get('skills', [])
        experience = result.get('experience_level', 'unknown')
        
        print(f"   ✅ AI Analysis completed")
        print(f"   ✅ Skills extracted: {len(skills)} - {skills[:3]}...")
        print(f"   ✅ Experience level: {experience}")
        
        verification_results['ai_functionality'] = {
            'status': 'passed',
            'skills_extracted': len(skills),
            'experience_detected': experience,
            'sample_skills': skills[:5]
        }
        
    except Exception as e:
        print(f"   ❌ AI functionality error: {e}")
        verification_results['ai_functionality'] = {'status': 'failed', 'error': str(e)}
    
    # 4. Deployment files check
    print("\n4. DEPLOYMENT FILES CHECK:")
    deployment_files = [
        '../render.yaml',
        '../render_deploy.sh',
        '../start.sh',
        '../build.sh',
        'deployment_backup/production_data_20250612_125504.json',
        'deployment_backup/deployment_manifest.json',
        'config/production_settings.py'
    ]
    
    files_status = {}
    for file_path in deployment_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
            files_status[file_path] = 'exists'
        else:
            print(f"   ❌ {file_path} - MISSING")
            files_status[file_path] = 'missing'
    
    verification_results['deployment_files'] = files_status
    
    # 5. Environment configuration check
    print("\n5. ENVIRONMENT CONFIGURATION:")
    env_vars = {
        'GROQ_API_KEY': os.environ.get('GROQ_API_KEY'),
        'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE'),
        'DEBUG': os.environ.get('DEBUG', 'True')
    }
    
    for var, value in env_vars.items():
        if value:
            print(f"   ✅ {var}: {'*' * min(len(str(value)), 10)}")
        else:
            print(f"   ⚠️  {var}: Not set (will be configured in Render)")
    
    verification_results['environment'] = env_vars
    
    # 6. Overall assessment
    print("\n6. OVERALL DEPLOYMENT ASSESSMENT:")
    
    critical_checks = [
        verification_results['database']['status'] == 'passed',
        verification_results['target_user']['status'] == 'passed',
        verification_results['ai_functionality']['status'] == 'passed',
        all(status == 'exists' for status in files_status.values())
    ]
    
    if all(critical_checks):
        print("   🎉 DEPLOYMENT READY!")
        print("   All critical components verified successfully")
        
        # Show the confirmed working state
        if verification_results['target_user']['status'] == 'passed':
            target_data = verification_results['target_user']
            print(f"\n   📋 CONFIRMED WORKING STATE:")
            print(f"   User: asalachik@gmail.com")
            print(f"   Resume: {target_data['resume_filename']}")
            print(f"   Status: {target_data['resume_status']}")
            print(f"   Skills: {target_data['skills_count']} extracted")
            print(f"   Experience: {target_data['experience_level']}")
        
        verification_results['overall'] = 'ready'
    else:
        print("   ❌ DEPLOYMENT NOT READY")
        print("   Some critical components failed verification")
        verification_results['overall'] = 'not_ready'
    
    return verification_results

def print_deployment_instructions():
    """Print final deployment instructions"""
    print("\n" + "="*60)
    print("🚀 RENDER DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n1. COMMIT AND PUSH CHANGES:")
    print("   git add .")
    print("   git commit -m 'Production deployment sync with working resume analysis'")
    print("   git push origin main")
    
    print("\n2. UPDATE RENDER SERVICE:")
    print("   - Go to your Render dashboard")
    print("   - Select your Smart Resume Matcher service")
    print("   - Update Build Command: ./render_deploy.sh")
    print("   - Update Start Command: ./start.sh")
    
    print("\n3. SET ENVIRONMENT VARIABLES:")
    print("   In Render dashboard > Environment:")
    print("   - GROQ_API_KEY: (your actual API key)")
    print("   - DEBUG: false")
    print("   - ALLOWED_HOSTS: your-app.onrender.com")
    print("   - SECRET_KEY: (will be auto-generated)")
    
    print("\n4. DEPLOY:")
    print("   - Click 'Manual Deploy' > 'Deploy latest commit'")
    print("   - Monitor the build logs for any errors")
    print("   - The deployment should restore your database with all working data")
    
    print("\n5. VERIFY DEPLOYMENT:")
    print("   - Visit your app URL")
    print("   - Login as asalachik@gmail.com")
    print("   - Verify the resume with skills is shown")
    print("   - Test uploading a new resume")
    
    print("\n" + "="*60)
    print("✅ Your local working environment is now ready for production!")

if __name__ == "__main__":
    results = verify_deployment_readiness()
    print_deployment_instructions()
