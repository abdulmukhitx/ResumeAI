"""
Universal Skills Database for All Professions
Comprehensive skills categorization for global resume analysis
"""

# Universal Skills Database organized by profession category
UNIVERSAL_SKILLS_DATABASE = {
    # Technology & IT
    'technology': {
        'programming_languages': [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
            'go', 'rust', 'scala', 'perl', 'r', 'matlab', 'sql', 'html', 'css', 'sass', 'less'
        ],
        'frameworks_libraries': [
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel', 'express', 'node.js',
            'bootstrap', 'tailwind', 'jquery', 'redux', 'gatsby', 'next.js', 'nuxt.js'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra', 'elasticsearch',
            'firebase', 'dynamodb', 'mariadb', 'neo4j'
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
            'terraform', 'ansible', 'vagrant', 'heroku', 'netlify', 'vercel'
        ],
        'tools_software': [
            'jira', 'confluence', 'slack', 'trello', 'asana', 'visual studio', 'intellij', 'eclipse',
            'postman', 'swagger', 'figma', 'sketch', 'adobe creative suite'
        ]
    },
    
    # Healthcare & Medical
    'healthcare': {
        'clinical_skills': [
            'patient assessment', 'iv therapy', 'wound care', 'medication administration', 'vital signs monitoring',
            'blood pressure measurement', 'injection techniques', 'catheter insertion', 'cpr', 'bls', 'acls', 'pals',
            'first aid', 'phlebotomy', 'electrocardiogram', 'ecg', 'ekg', 'ultrasound', 'x-ray interpretation'
        ],
        'medical_specialties': [
            'pediatrics', 'cardiology', 'neurology', 'oncology', 'emergency medicine', 'internal medicine',
            'surgery', 'orthopedics', 'psychiatry', 'dermatology', 'radiology', 'anesthesiology',
            'obstetrics', 'gynecology', 'geriatrics', 'intensive care', 'critical care'
        ],
        'medical_equipment': [
            'ventilator', 'defibrillator', 'cardiac monitor', 'infusion pump', 'glucometer', 'pulse oximeter',
            'stethoscope', 'otoscope', 'ophthalmoscope', 'sphygmomanometer', 'nebulizer', 'suction device'
        ],
        'health_records': [
            'epic', 'cerner', 'allscripts', 'athenahealth', 'meditech', 'nextgen', 'ehr', 'emr',
            'electronic health records', 'medical coding', 'icd-10', 'cpt codes', 'hipaa compliance'
        ],
        'nursing_skills': [
            'patient care', 'medication management', 'infection control', 'discharge planning', 'patient education',
            'family communication', 'pain management', 'mobility assistance', 'nutritional assessment'
        ]
    },
    
    # Legal & Law
    'legal': {
        'practice_areas': [
            'corporate law', 'criminal law', 'civil litigation', 'intellectual property', 'employment law',
            'real estate law', 'family law', 'immigration law', 'tax law', 'environmental law',
            'bankruptcy law', 'personal injury', 'contract law', 'securities law', 'mergers and acquisitions'
        ],
        'legal_skills': [
            'legal research', 'brief writing', 'contract drafting', 'deposition', 'trial advocacy',
            'legal writing', 'case analysis', 'statutory interpretation', 'regulatory compliance',
            'due diligence', 'negotiation', 'mediation', 'arbitration'
        ],
        'legal_software': [
            'westlaw', 'lexisnexis', 'clio', 'mycase', 'practice panther', 'timeslips', 'quickbooks legal',
            'ediscovery', 'relativity', 'concordance', 'summation'
        ],
        'court_procedures': [
            'motion practice', 'discovery', 'pleadings', 'appeals', 'oral argument', 'cross-examination',
            'witness preparation', 'jury selection', 'settlement negotiation'
        ]
    },
    
    # Education & Teaching
    'education': {
        'teaching_methods': [
            'curriculum development', 'lesson planning', 'classroom management', 'differentiated instruction',
            'assessment design', 'educational technology', 'student engagement', 'inclusive education',
            'project-based learning', 'collaborative learning', 'online teaching', 'hybrid learning'
        ],
        'subject_areas': [
            'mathematics', 'science', 'english', 'history', 'geography', 'physical education',
            'art', 'music', 'foreign languages', 'computer science', 'special education', 'early childhood education'
        ],
        'educational_tools': [
            'google classroom', 'canvas', 'blackboard', 'moodle', 'zoom', 'teams', 'kahoot', 'padlet',
            'flipgrid', 'nearpod', 'edmodo', 'schoology', 'gradebook', 'powerschool'
        ],
        'educational_skills': [
            'student assessment', 'parent communication', 'iep development', '504 plans', 'behavior management',
            'data analysis', 'professional development', 'mentoring', 'tutoring', 'educational research'
        ]
    },
    
    # Finance & Accounting
    'finance': {
        'accounting_skills': [
            'financial reporting', 'budgeting', 'forecasting', 'accounts payable', 'accounts receivable',
            'general ledger', 'journal entries', 'reconciliation', 'cost accounting', 'tax preparation',
            'audit', 'compliance', 'financial analysis', 'variance analysis'
        ],
        'financial_software': [
            'quickbooks', 'sage', 'sap', 'oracle financials', 'excel', 'peachtree', 'xero', 'freshbooks',
            'wave accounting', 'zoho books', 'netsuite', 'dynamics 365'
        ],
        'investment_banking': [
            'financial modeling', 'valuation', 'mergers and acquisitions', 'capital markets', 'equity research',
            'debt financing', 'ipo', 'due diligence', 'pitch book preparation', 'risk management'
        ],
        'certifications': [
            'cpa', 'cfa', 'cma', 'cia', 'frm', 'cfp', 'series 7', 'series 66', 'acca', 'caia'
        ]
    },
    
    # Marketing & Sales
    'marketing': {
        'digital_marketing': [
            'seo', 'sem', 'social media marketing', 'content marketing', 'email marketing', 'ppc',
            'google ads', 'facebook ads', 'linkedin ads', 'analytics', 'conversion optimization',
            'marketing automation', 'lead generation', 'growth hacking'
        ],
        'marketing_tools': [
            'google analytics', 'hubspot', 'salesforce', 'mailchimp', 'hootsuite', 'buffer', 'canva',
            'adobe creative suite', 'wordpress', 'shopify', 'marketo', 'pardot', 'klaviyo'
        ],
        'sales_skills': [
            'lead qualification', 'prospecting', 'cold calling', 'relationship building', 'negotiation',
            'closing techniques', 'account management', 'territory management', 'sales forecasting',
            'crm management', 'pipeline management'
        ],
        'brand_marketing': [
            'brand strategy', 'brand positioning', 'market research', 'competitive analysis',
            'campaign development', 'creative direction', 'public relations', 'event marketing'
        ]
    },
    
    # Human Resources
    'human_resources': {
        'hr_functions': [
            'recruitment', 'talent acquisition', 'employee relations', 'performance management',
            'compensation and benefits', 'training and development', 'hr analytics', 'succession planning',
            'employee engagement', 'diversity and inclusion', 'change management'
        ],
        'hr_software': [
            'workday', 'adp', 'bamboohr', 'cornerstone ondemand', 'successfactors', 'greenhouse',
            'lever', 'indeed', 'linkedin recruiter', 'taleo', 'kronos', 'paycom'
        ],
        'compliance': [
            'employment law', 'eeoc compliance', 'fmla', 'ada compliance', 'wage and hour laws',
            'safety regulations', 'osha', 'workers compensation', 'unemployment insurance'
        ]
    },
    
    # Operations & Manufacturing
    'operations': {
        'manufacturing': [
            'lean manufacturing', 'six sigma', 'quality control', 'process improvement', 'production planning',
            'inventory management', 'supply chain', 'logistics', 'warehouse management', 'safety protocols'
        ],
        'project_management': [
            'agile', 'scrum', 'waterfall', 'kanban', 'risk management', 'stakeholder management',
            'resource planning', 'timeline management', 'budget management', 'team leadership'
        ],
        'tools': [
            'microsoft project', 'jira', 'asana', 'trello', 'monday.com', 'smartsheet', 'basecamp',
            'slack', 'teams', 'confluence', 'notion'
        ]
    },
    
    # Customer Service & Support
    'customer_service': {
        'service_skills': [
            'customer support', 'technical support', 'troubleshooting', 'problem resolution',
            'customer retention', 'escalation management', 'communication skills', 'empathy',
            'active listening', 'conflict resolution', 'product knowledge'
        ],
        'support_tools': [
            'zendesk', 'freshdesk', 'intercom', 'helpscout', 'salesforce service cloud',
            'servicenow', 'jira service desk', 'kayako', 'desk.com', 'livechat'
        ]
    },
    
    # Creative & Design
    'creative': {
        'design_skills': [
            'graphic design', 'web design', 'ui/ux design', 'logo design', 'branding', 'typography',
            'color theory', 'layout design', 'print design', 'digital illustration', 'photography',
            'video editing', 'motion graphics', '3d modeling', 'animation'
        ],
        'design_software': [
            'adobe photoshop', 'adobe illustrator', 'adobe indesign', 'adobe after effects',
            'adobe premiere', 'sketch', 'figma', 'invision', 'canva', 'procreate', 'blender',
            'maya', 'cinema 4d', 'final cut pro'
        ]
    },
    
    # Research & Analytics
    'research': {
        'research_methods': [
            'quantitative research', 'qualitative research', 'data collection', 'survey design',
            'statistical analysis', 'data visualization', 'research design', 'literature review',
            'hypothesis testing', 'experimental design', 'case study', 'ethnography'
        ],
        'analytics_tools': [
            'spss', 'r', 'python', 'tableau', 'power bi', 'google analytics', 'excel',
            'stata', 'sas', 'matlab', 'nvivo', 'atlas.ti', 'surveymonkey', 'qualtrics'
        ]
    }
}

# Experience level mappings for different professions
EXPERIENCE_LEVELS = {
    'universal': ['entry', 'junior', 'mid', 'senior', 'lead', 'principal', 'director', 'executive'],
    'healthcare': ['student', 'intern', 'resident', 'fellow', 'attending', 'chief', 'director'],
    'legal': ['law student', 'paralegal', 'associate', 'senior associate', 'counsel', 'partner', 'managing partner'],
    'education': ['student teacher', 'substitute', 'teacher', 'senior teacher', 'department head', 'principal', 'superintendent'],
    'finance': ['analyst', 'associate', 'vice president', 'director', 'managing director', 'partner'],
    'academic': ['undergraduate', 'graduate student', 'phd candidate', 'postdoc', 'assistant professor', 'associate professor', 'professor']
}

# Job title patterns for different professions
JOB_TITLE_PATTERNS = {
    'technology': [
        'developer', 'engineer', 'programmer', 'architect', 'analyst', 'administrator', 'manager',
        'lead', 'senior', 'junior', 'full stack', 'backend', 'frontend', 'devops', 'qa', 'tester'
    ],
    'healthcare': [
        'nurse', 'doctor', 'physician', 'therapist', 'technician', 'assistant', 'coordinator',
        'specialist', 'practitioner', 'clinician', 'surgeon', 'resident', 'intern', 'fellow'
    ],
    'legal': [
        'attorney', 'lawyer', 'counsel', 'paralegal', 'legal assistant', 'associate', 'partner',
        'solicitor', 'barrister', 'judge', 'clerk', 'investigator'
    ],
    'education': [
        'teacher', 'professor', 'instructor', 'educator', 'tutor', 'principal', 'dean',
        'coordinator', 'administrator', 'counselor', 'librarian', 'coach'
    ],
    'finance': [
        'accountant', 'analyst', 'advisor', 'planner', 'manager', 'director', 'controller',
        'treasurer', 'auditor', 'consultant', 'associate', 'vice president'
    ],
    'marketing': [
        'manager', 'coordinator', 'specialist', 'analyst', 'strategist', 'director',
        'executive', 'associate', 'representative', 'consultant'
    ],
    'sales': [
        'representative', 'manager', 'director', 'executive', 'associate', 'coordinator',
        'specialist', 'consultant', 'agent', 'advisor'
    ]
}

def get_all_skills():
    """Get all skills from all categories"""
    all_skills = []
    for category, subcategories in UNIVERSAL_SKILLS_DATABASE.items():
        for subcategory, skills in subcategories.items():
            all_skills.extend(skills)
    return all_skills

def get_skills_by_category(category):
    """Get skills for a specific category"""
    if category in UNIVERSAL_SKILLS_DATABASE:
        skills = []
        for subcategory, skill_list in UNIVERSAL_SKILLS_DATABASE[category].items():
            skills.extend(skill_list)
        return skills
    return []

def identify_profession_category(resume_text, job_titles=None):
    """Identify the most likely profession category based on resume content"""
    resume_lower = resume_text.lower()
    job_titles_lower = [title.lower() for title in (job_titles or [])]
    
    category_scores = {}
    
    # Score based on skills mentioned
    for category, subcategories in UNIVERSAL_SKILLS_DATABASE.items():
        score = 0
        for subcategory, skills in subcategories.items():
            for skill in skills:
                if skill.lower() in resume_lower:
                    score += 1
        category_scores[category] = score
    
    # Score based on job titles
    for category, title_patterns in JOB_TITLE_PATTERNS.items():
        for title in job_titles_lower:
            for pattern in title_patterns:
                if pattern in title:
                    category_scores[category] = category_scores.get(category, 0) + 2
    
    # Return the category with highest score, default to 'technology' if no clear match
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category
    
    return 'technology'  # Default fallback

def get_profession_search_terms(profession_category, job_titles=None, skills=None):
    """
    Get search terms for job matching based on profession category
    
    Args:
        profession_category: The identified profession category
        job_titles: List of job titles from resume
        skills: List of skills from resume
    
    Returns:
        List of search terms optimized for the profession
    """
    # Base search terms for each profession
    profession_search_terms = {
        'healthcare': ['nurse', 'doctor', 'physician', 'medical', 'healthcare', 'clinical', 'hospital', 'clinic'],
        'legal': ['lawyer', 'attorney', 'legal', 'law', 'paralegal', 'counsel', 'litigation', 'contract'],
        'education': ['teacher', 'instructor', 'educator', 'professor', 'tutor', 'academic', 'curriculum', 'learning'],
        'finance': ['accountant', 'financial', 'analyst', 'banking', 'investment', 'audit', 'tax', 'finance'],
        'marketing': ['marketing', 'advertising', 'campaign', 'brand', 'digital marketing', 'social media', 'content'],
        'sales': ['sales', 'account manager', 'business development', 'client relations', 'revenue', 'target'],
        'hr': ['human resources', 'hr', 'recruiter', 'talent acquisition', 'benefits', 'payroll', 'employee'],
        'operations': ['operations', 'logistics', 'supply chain', 'project manager', 'process improvement'],
        'customer_service': ['customer service', 'support', 'help desk', 'client support', 'call center'],
        'creative': ['designer', 'creative', 'graphic', 'ui/ux', 'artist', 'content creator', 'photography'],
        'research': ['researcher', 'analyst', 'data scientist', 'research', 'analysis', 'statistics'],
        'technology': ['developer', 'engineer', 'programmer', 'software', 'technical', 'IT', 'system admin']
    }
    
    # Get base terms for the profession
    search_terms = profession_search_terms.get(profession_category, ['professional'])
    
    # Add job titles if available
    if job_titles:
        search_terms.extend(job_titles[:3])  # Add top 3 job titles
    
    # Add relevant skills as search terms
    if skills:
        # Add up to 3 most relevant skills
        search_terms.extend(skills[:3])
    
    return search_terms


def get_all_skills_for_profession(profession_category):
    """
    Get all skills for a specific profession category
    
    Args:
        profession_category: The profession category
    
    Returns:
        Set of all skills for that profession
    """
    if profession_category not in UNIVERSAL_SKILLS_DATABASE:
        return set()
    
    all_skills = set()
    for skills in UNIVERSAL_SKILLS_DATABASE[profession_category].values():
        all_skills.update([skill.lower() for skill in skills])
    
    return all_skills
