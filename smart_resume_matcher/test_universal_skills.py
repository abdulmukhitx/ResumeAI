#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
sys.path.append('/home/abdulmukhit/Desktop/ResumeAI/smart_resume_matcher')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from resumes.utils import AIAnalyzer
from resumes.universal_skills import get_all_skills

print("=== Testing Universal Skills Support ===")
print(f"Number of skills in universal database: {len(get_all_skills())}")

# Test with nursing resume
nursing_sample = """
Sarah Johnson, RN
Registered Nurse
Email: sarah.j@email.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Dedicated Registered Nurse with 5 years of experience in pediatric care, patient assessment, 
and emergency response. Skilled in IV therapy, wound care, and medication administration.

EXPERIENCE
Senior Pediatric Nurse
Children's Hospital, Boston, MA
2020 - Present
• Perform pediatric assessments and vital signs monitoring
• Administer medications and IV therapy
• Provide wound care and patient education
• Collaborate with multidisciplinary healthcare teams

Staff Nurse
General Hospital, Boston, MA
2019 - 2020  
• Provided direct patient care in medical-surgical unit
• Documented patient information in Epic EHR system
• Assisted with emergency procedures and CPR

EDUCATION
Bachelor of Science in Nursing
Boston University School of Nursing, 2019

CERTIFICATIONS & SKILLS
• BLS, ACLS, PALS certified
• IV therapy, wound care, medication administration
• Epic, Cerner, MEDITECH
• Pediatric assessment, vital signs monitoring
"""

print("\n=== Testing Nursing Resume Analysis ===")
analyzer = AIAnalyzer()
result = analyzer._fallback_analysis(nursing_sample)

print("Skills found:", result.get('skills', []))
print("Job titles:", result.get('job_titles', []))
print("Experience level:", result.get('experience_level'))
print("Education:", result.get('education', []))

# Test with legal resume
legal_sample = """
Michael Davis, Esq.
Corporate Attorney
Email: m.davis@lawfirm.com | Phone: (555) 987-6543

PROFESSIONAL SUMMARY
Experienced Corporate Attorney with 8 years specializing in contract law, mergers and acquisitions, 
and regulatory compliance. Skilled in legal research, document review, and client counseling.

EXPERIENCE
Senior Associate Attorney
BigLaw Firm, New York, NY
2018 - Present
• Draft and negotiate commercial contracts and M&A agreements
• Conduct legal research using Westlaw and LexisNexis
• Advise clients on regulatory compliance and corporate governance
• Manage due diligence processes for acquisitions

Junior Associate
Mid-size Law Firm, New York, NY
2016 - 2018
• Performed contract review and legal analysis
• Assisted with litigation support and document discovery
• Prepared legal briefs and memoranda

EDUCATION
Juris Doctor (JD)
Harvard Law School, 2016

Bachelor of Arts in Political Science
Yale University, 2013

BAR ADMISSIONS & SKILLS
• New York State Bar, Connecticut Bar
• Contract law, M&A, regulatory compliance
• Westlaw, LexisNexis, document review
• Legal research, brief writing, client counseling
"""

print("\n=== Testing Legal Resume Analysis ===")
result = analyzer._fallback_analysis(legal_sample)

print("Skills found:", result.get('skills', []))
print("Job titles:", result.get('job_titles', []))
print("Experience level:", result.get('experience_level'))
print("Education:", result.get('education', []))

print("\n=== Test completed successfully! ===")
