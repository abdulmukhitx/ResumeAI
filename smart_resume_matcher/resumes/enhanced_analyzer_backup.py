"""
Enhanced AI Resume Analyzer with Improved Skill Extraction and Job Matching
"""

import re
import json
import requests
import logging
from typing import Dict, List, Any, Tuple
from django.conf import settings
from .utils import PDFProcessor

logger = logging.getLogger(__name__)

class EnhancedAIAnalyzer:
    """
    Advanced AI analyzer with improved skill extraction and intelligent job matching
    """
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = settings.GROQ_API_URL
        
        # Enhanced skill categories with specific technologies
        self.skill_categories = {
            'programming_languages': [
                'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 
                'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'C', 'Objective-C', 'Dart',
                'Perl', 'Shell', 'Bash', 'PowerShell', 'Assembly', 'Clojure', 'F#', 'Haskell'
            ],
            'web_frameworks': [
                'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI', 'Express.js', 
                'Node.js', 'Next.js', 'Nuxt.js', 'Laravel', 'Spring Boot', 'ASP.NET', 
                'Ruby on Rails', 'Symfony', 'CodeIgniter', 'Svelte', 'Ember.js'
            ],
            'databases': [
                'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
                'MariaDB', 'DynamoDB', 'Cassandra', 'Elasticsearch', 'Neo4j', 'InfluxDB',
                'CouchDB', 'Firebase', 'Supabase', 'PlanetScale', 'Snowflake'
            ],
            'cloud_platforms': [
                'AWS', 'Google Cloud', 'Azure', 'DigitalOcean', 'Heroku', 'Vercel', 'Netlify',
                'Firebase', 'Cloudflare', 'Linode', 'Vultr', 'IBM Cloud', 'Oracle Cloud'
            ],
            'devops_tools': [
                'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform',
                'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Nginx', 'Apache', 'Git', 'SVN',
                'CircleCI', 'Travis CI', 'Helm', 'Prometheus', 'Grafana', 'ELK Stack'
            ],
            'mobile_development': [
                'React Native', 'Flutter', 'Ionic', 'Xamarin', 'Swift', 'Kotlin', 'Cordova',
                'PhoneGap', 'NativeScript', 'Unity', 'Unreal Engine'
            ],
            'data_science': [
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib',
                'Seaborn', 'Jupyter', 'Apache Spark', 'Hadoop', 'Kafka', 'Airflow',
                'MLflow', 'Kubeflow', 'SageMaker', 'BigQuery', 'Tableau', 'Power BI'
            ],
            'design_tools': [
                'Figma', 'Adobe XD', 'Sketch', 'InVision', 'Photoshop', 'Illustrator',
                'After Effects', 'Premiere Pro', 'Canva', 'Framer', 'Principle'
            ],
            'project_management': [
                'Jira', 'Trello', 'Asana', 'Monday.com', 'Notion', 'Confluence', 'Slack',
                'Microsoft Teams', 'Zoom', 'Linear', 'ClickUp', 'Basecamp'
            ]
        }
        
        # Technology stack combinations for better matching
        self.tech_stacks = {
            'fullstack_web': ['React', 'Node.js', 'Express.js', 'MongoDB', 'PostgreSQL'],
            'python_backend': ['Python', 'Django', 'Flask', 'FastAPI', 'PostgreSQL', 'Redis'],
            'frontend_react': ['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'Redux'],
            'data_science': ['Python', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Jupyter'],
            'devops': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform', 'Git'],
            'mobile': ['React Native', 'Flutter', 'Swift', 'Kotlin'],
            'java_enterprise': ['Java', 'Spring Boot', 'Maven', 'PostgreSQL', 'Docker']
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        return PDFProcessor.extract_text_from_pdf(file_path)

    def enhanced_skill_extraction(self, text: str) -> Dict[str, List[str]]:
        """
        Enhanced skill extraction with context awareness and specificity scoring
        """
        text_lower = text.lower()
        extracted_skills = {}
        
        for category, skills in self.skill_categories.items():
            category_skills = []
            
            for skill in skills:
                skill_lower = skill.lower()
                
                # Multiple detection patterns with context
                patterns = [
                    # Exact word boundary matches
                    rf'\b{re.escape(skill_lower)}\b',
                    # Technology with version numbers
                    rf'{re.escape(skill_lower)}\s*(?:\d+|\d+\.\d+|v\d+)',
                    # Technology with common suffixes
                    rf'{re.escape(skill_lower)}(?:js|\.js|\.py|\.rb)?',
                    # Technology in lists or bullets
                    rf'(?:•|[\-\*])\s*{re.escape(skill_lower)}\b',
                    # Technology with context words
                    rf'(?:using|with|in|built with|developed with|worked with|experience with|proficient in)\s+{re.escape(skill_lower)}\b',
                    rf'{re.escape(skill_lower)}\s+(?:development|programming|framework|library|database|platform|tool)',
                    # Years of experience patterns
                    rf'(?:\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{re.escape(skill_lower)}\b',
                ]
                
                skill_found = False
                context_score = 0
                
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        skill_found = True
                        context_score += len(matches) * 0.3
                
                if skill_found:
                    # Additional context scoring
                    context_score += self._calculate_skill_context_score(text_lower, skill_lower)
                    
                    # Only include if context score is high enough
                    if context_score >= 0.4:  # Stricter threshold
                        category_skills.append(skill)
            
            if category_skills:
                extracted_skills[category] = category_skills
        
        return extracted_skills

    def _calculate_skill_context_score(self, text: str, skill: str) -> float:
        """
        Calculate how relevant a skill is based on context
        """
        # Look for skill mentions with relevant context words
        context_patterns = [
            rf'{skill}\s+(?:development|programming|experience|expertise|proficient)',
            rf'(?:experienced|skilled|proficient)\s+(?:in|with)\s+{skill}',
            rf'(?:using|worked with|developed with)\s+{skill}',
            rf'{skill}\s+(?:framework|library|tool|platform)',
            rf'(?:\d+)\s+(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{skill}',
        ]
        
        score = 0.0
        for pattern in context_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 0.2  # Each contextual mention adds weight
        
        # Boost score if skill appears multiple times
        mentions = len(re.findall(rf'\b{skill}\b', text, re.IGNORECASE))
        score += min(mentions * 0.1, 0.5)  # Cap at 0.5 for multiple mentions
        
        return min(score, 1.0)  # Cap at 1.0

    def identify_tech_stacks(self, skills: Dict[str, List[str]]) -> List[str]:
        """
        Identify technology stacks based on extracted skills
        """
        all_skills = []
        for category_skills in skills.values():
            all_skills.extend([s.lower() for s in category_skills])
        
        identified_stacks = []
        
        for stack_name, stack_skills in self.tech_stacks.items():
            stack_skills_lower = [s.lower() for s in stack_skills]
            matching_skills = set(all_skills) & set(stack_skills_lower)
            
            # If at least 60% of stack skills are present, consider it a match
            if len(matching_skills) >= len(stack_skills_lower) * 0.6:
                identified_stacks.append(stack_name.replace('_', ' ').title())
        
        return identified_stacks

    def enhanced_experience_analysis(self, text: str) -> Dict[str, Any]:
        """
        Enhanced experience level analysis with multiple factors
        """
        text_lower = text.lower()
        
        # Extract years of experience
        years_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience\s*(?:of|:)?\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|with|of)',
        ]
        
        years = 0
        for pattern in years_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = max([int(m) for m in matches] + [years])
        
        # Look for seniority indicators
        seniority_indicators = {
            'senior': r'senior|sr\.|lead|principal|staff|architect',
            'middle': r'mid-level|intermediate|associate',
            'junior': r'junior|jr\.|entry|intern|graduate|trainee'
        }
        
        seniority_scores = {}
        for level, pattern in seniority_indicators.items():
            matches = len(re.findall(pattern, text_lower))
            seniority_scores[level] = matches
        
        # Count management/leadership indicators
        leadership_patterns = [
            r'team lead|tech lead|engineering manager|cto|vp|director',
            r'managed\s+\d+\s+(?:people|developers|engineers)',
            r'mentored|guided|supervised',
        ]
        
        leadership_score = sum(len(re.findall(p, text_lower)) for p in leadership_patterns)
        
        # Determine experience level
        if years >= 8 or leadership_score > 2 or seniority_scores.get('senior', 0) > 1:
            level = 'senior'
        elif years >= 4 or seniority_scores.get('middle', 0) > 0:
            level = 'middle'
        elif years >= 1 or seniority_scores.get('junior', 0) > 0:
            level = 'junior'
        else:
            level = 'entry'
        
        return {
            'level': level,
            'years': years,
            'leadership_score': leadership_score,
            'confidence': min((years * 0.1) + (leadership_score * 0.2) + 0.5, 1.0)
        }

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Enhanced resume analysis with improved AI prompts and fallback
        """
        logger.info("Starting enhanced resume analysis")
        
        # First, try enhanced AI analysis
        if self.api_key and self.api_key != 'your-groq-api-key':
            try:
                return self._enhanced_ai_analysis(resume_text)
            except Exception as e:
                logger.warning(f"AI analysis failed, using enhanced fallback: {e}")
        
        # Use enhanced fallback analysis
        return self._enhanced_fallback_analysis(resume_text)

    def _enhanced_ai_analysis(self, resume_text: str) -> Dict[str, Any]:
        """
        Enhanced AI analysis with better prompts for specific skill extraction
        """
        prompt = f"""
        You are an expert technical recruiter analyzing resumes for technology companies. Your job is to extract SPECIFIC, CONCRETE skills and technologies mentioned in the resume text.

        CRITICAL RULES:
        1. Extract ONLY technologies explicitly mentioned in the text
        2. Use EXACT names (e.g., "PostgreSQL", not "SQL database")
        3. Don't infer or assume skills not clearly stated
        4. Focus on specific frameworks, tools, and technologies
        5. Group similar technologies appropriately
        6. Identify the candidate's PRIMARY technology focus area

        Resume Text:
        {resume_text}

        ANALYZE THIS RESUME and extract structured information:

        Return a JSON object with this EXACT structure:
        {{
            "extracted_skills": ["Complete list of ALL specific technologies mentioned"],
            "programming_languages": ["Only programming languages: Python, JavaScript, Java, etc."],
            "frameworks_libraries": ["Specific frameworks: Django, React, Angular, Spring Boot, etc."],
            "databases": ["Specific databases: PostgreSQL, MongoDB, MySQL, Redis, etc."],
            "cloud_platforms": ["Cloud services: AWS, Google Cloud, Azure, etc."],
            "tools_technologies": ["Development tools: Docker, Kubernetes, Git, Jenkins, etc."],
            "experience_level": "entry/junior/middle/senior/lead",
            "years_of_experience": 0,
            "job_titles": ["Actual job titles from experience section"],
            "tech_stack_focus": "Primary technology area (e.g., 'Python/Django Backend', 'React Frontend', 'Full-Stack JavaScript', 'Data Science', 'DevOps/Cloud', 'Mobile Development')",
            "specialization": "Main area of expertise based on skills and experience",
            "seniority_level": "Based on job titles and experience",
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school name", 
                    "year": "graduation year"
                }}
            ],
            "work_experience": [
                {{
                    "position": "job title",
                    "company": "company name",
                    "duration": "time period",
                    "key_technologies": ["technologies used in this specific role"]
                }}
            ],
            "professional_summary": "Brief technical summary emphasizing specific skills and experience",
            "confidence_score": 0.95
        }}

        SKILL EXTRACTION GUIDELINES:
        - Python web development: Look for Django, Flask, FastAPI, SQLAlchemy
        - JavaScript development: Look for React, Vue, Angular, Node.js, Express
        - Database technologies: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
        - Cloud/DevOps: AWS services (EC2, S3, RDS), Docker, Kubernetes, Jenkins
        - Mobile: React Native, Flutter, Swift, Kotlin, Ionic
        - Data Science: Pandas, NumPy, TensorFlow, PyTorch, Scikit-learn

        EXPERIENCE LEVEL DETERMINATION:
        - entry: 0-1 years or intern/graduate roles
        - junior: 1-3 years or junior developer titles
        - middle: 3-6 years or regular developer titles  
        - senior: 6+ years or senior/lead titles
        - lead: Team lead, architect, or management roles

        TECH STACK FOCUS EXAMPLES:
        - "Python/Django Backend" for Django + PostgreSQL + REST APIs
        - "React Frontend" for React + TypeScript + modern CSS
        - "Full-Stack JavaScript" for React + Node.js + MongoDB
        - "Data Science" for Python + Pandas + ML libraries
        - "DevOps/Cloud" for Docker + Kubernetes + AWS
        - "Mobile Development" for React Native or Flutter

        Return ONLY the JSON object, no additional text or explanations.
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'llama3-70b-8192',  # Use the more capable model
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert technical resume analyzer. Extract specific technologies and skills with high precision. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 3000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        
        # Clean and parse JSON
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = ai_response
        
        # Extract JSON object if embedded
        if not json_str.strip().startswith('{'):
            json_block_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
            if json_block_match:
                json_str = json_block_match.group(1)
        
        parsed_data = json.loads(json_str)
        
        # Post-process to ensure consistency
        parsed_data = self._post_process_ai_results(parsed_data)
        
        logger.info(f"Enhanced AI analysis completed with confidence: {parsed_data.get('confidence_score', 0)}")
        return parsed_data
            "experience_level": "entry/junior/middle/senior/lead",
            "years_of_experience": 0,
            "job_titles": ["Actual job titles from experience section"],
            "tech_stack_focus": "Primary technology area (e.g., 'Python/Django Backend', 'React Frontend', 'Full-Stack JavaScript', 'Data Science', 'DevOps/Cloud', 'Mobile Development')",
            "specialization": "Main area of expertise based on skills and experience",
            "seniority_level": "Based on job titles and experience",
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school name", 
                    "year": "graduation year"
                }}
            ],
            "work_experience": [
                {{
                    "position": "job title",
                    "company": "company name",
                    "duration": "time period",
                    "key_technologies": ["technologies used in this specific role"]
                }}
            ],
            "professional_summary": "Brief technical summary emphasizing specific skills and experience",
            "confidence_score": 0.95
        }}

        SKILL EXTRACTION GUIDELINES:
        - Python web development: Look for Django, Flask, FastAPI, SQLAlchemy
        - JavaScript development: Look for React, Vue, Angular, Node.js, Express
        - Database technologies: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
        - Cloud/DevOps: AWS services (EC2, S3, RDS), Docker, Kubernetes, Jenkins
        - Mobile: React Native, Flutter, Swift, Kotlin, Ionic
        - Data Science: Pandas, NumPy, TensorFlow, PyTorch, Scikit-learn

        EXPERIENCE LEVEL DETERMINATION:
        - entry: 0-1 years or intern/graduate roles
        - junior: 1-3 years or junior developer titles
        - middle: 3-6 years or regular developer titles  
        - senior: 6+ years or senior/lead titles
        - lead: Team lead, architect, or management roles

        TECH STACK FOCUS EXAMPLES:
        - "Python/Django Backend" for Django + PostgreSQL + REST APIs
        - "React Frontend" for React + TypeScript + modern CSS
        - "Full-Stack JavaScript" for React + Node.js + MongoDB
        - "Data Science" for Python + Pandas + ML libraries
        - "DevOps/Cloud" for Docker + Kubernetes + AWS
        - "Mobile Development" for React Native or Flutter

        Return ONLY the JSON object, no additional text or explanations.
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'llama3-70b-8192',  # Use the more capable model
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert technical resume analyzer. Extract specific technologies and skills with high precision. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 3000
        }
        }
        
        data = {
            'model': 'llama3-70b-8192',  # Use the more capable model
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert technical resume analyzer. Extract specific technologies and skills with high precision. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 3000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        
        # Clean and parse JSON
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = ai_response
        
        # Extract JSON object if embedded
        if not json_str.strip().startswith('{'):
            json_block_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
            if json_block_match:
                json_str = json_block_match.group(1)
        
        parsed_data = json.loads(json_str)
        
        # Post-process to ensure consistency
        parsed_data = self._post_process_ai_results(parsed_data)
        
        logger.info(f"Enhanced AI analysis completed with confidence: {parsed_data.get('confidence_score', 0)}")
        return parsed_data

    def _enhanced_fallback_analysis(self, resume_text: str) -> Dict[str, Any]:
        """
        Enhanced fallback analysis with improved skill extraction
        """
        logger.info("Using enhanced fallback analysis")
        
        # Enhanced skill extraction
        skills_by_category = self.enhanced_skill_extraction(resume_text)
        
        # Flatten all skills
        all_skills = []
        for category_skills in skills_by_category.values():
            all_skills.extend(category_skills)
        
        # Experience analysis
        experience_analysis = self.enhanced_experience_analysis(resume_text)
        
        # Identify tech stacks
        tech_stacks = self.identify_tech_stacks(skills_by_category)
        
        # Determine specialization
        specialization = self._determine_specialization(skills_by_category, tech_stacks)
        
        return {
            'extracted_skills': all_skills,
            'programming_languages': skills_by_category.get('programming_languages', []),
            'frameworks_libraries': skills_by_category.get('web_frameworks', []),
            'databases': skills_by_category.get('databases', []),
            'cloud_platforms': skills_by_category.get('cloud_platforms', []),
            'tools_technologies': skills_by_category.get('devops_tools', []) + skills_by_category.get('project_management', []),
            'experience_level': experience_analysis['level'],
            'years_of_experience': experience_analysis['years'],
            'tech_stack_focus': tech_stacks[0] if tech_stacks else 'General Development',
            'specialization': specialization,
            'seniority_level': experience_analysis['level'],
            'confidence_score': experience_analysis['confidence'],
            'job_titles': self._extract_job_titles(resume_text),
            'education': self._extract_education(resume_text),
            'work_experience': self._extract_work_experience(resume_text),
            'professional_summary': self._generate_summary(all_skills, experience_analysis, specialization)
        }

    def _determine_specialization(self, skills_by_category: Dict[str, List[str]], tech_stacks: List[str]) -> str:
        """
        Determine the main specialization based on skills
        """
        if tech_stacks:
            return tech_stacks[0]
        
        # Count skills by category to determine focus
        category_counts = {cat: len(skills) for cat, skills in skills_by_category.items()}
        
        if category_counts.get('data_science', 0) > 2:
            return 'Data Science & Machine Learning'
        elif category_counts.get('mobile_development', 0) > 1:
            return 'Mobile Development'
        elif category_counts.get('devops_tools', 0) > 3:
            return 'DevOps & Cloud Engineering'
        elif category_counts.get('web_frameworks', 0) > 1:
            return 'Web Development'
        elif category_counts.get('programming_languages', 0) > 2:
            return 'Software Development'
        else:
            return 'Technology Professional'

    def _post_process_ai_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process AI results to ensure consistency and quality
        """
        # Ensure all required fields exist
        required_fields = [
            'extracted_skills', 'programming_languages', 'frameworks_libraries',
            'databases', 'cloud_platforms', 'tools_technologies', 'experience_level',
            'years_of_experience', 'tech_stack_focus', 'specialization',
            'confidence_score'
        ]
        
        for field in required_fields:
            if field not in data:
                data[field] = [] if field.endswith('s') and field != 'years_of_experience' else 'unknown'
        
        # Validate experience level
        valid_levels = ['entry', 'junior', 'middle', 'senior', 'lead']
        if data.get('experience_level') not in valid_levels:
            data['experience_level'] = 'junior'
        
        # Ensure confidence score is between 0 and 1
        confidence = data.get('confidence_score', 0.5)
        data['confidence_score'] = max(0.0, min(1.0, float(confidence)))
        
        return data

    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from resume text"""
        # Implementation similar to existing logic but enhanced
        titles = []
        
        title_patterns = [
            r'(Senior|Lead|Principal|Staff)\s+(Software|Full Stack|Backend|Frontend|Web|Mobile)\s+(Developer|Engineer)',
            r'(Software|Web|Mobile|Frontend|Backend|Full Stack)\s+(Developer|Engineer)',
            r'(Data|Machine Learning|AI)\s+(Scientist|Engineer)',
            r'(DevOps|Cloud|Platform|Site Reliability)\s+(Engineer)',
            r'(Product|Project|Engineering)\s+(Manager)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                title = ' '.join(match).strip()
                if title and title not in titles:
                    titles.append(title)
        
        return titles[:5]  # Limit to top 5

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        # Simplified education extraction
        education = []
        
        edu_patterns = [
            r'(Bachelor|Master|PhD|Doctor)\s+(?:of|in)?\s+([^\n]+)\n+([^\n]+(?:University|College)[^\n]*)\n+(\d{4})',
            r'(B\.?S|M\.?S|M\.?B\.?A|Ph\.?D)\.?\s+(?:in)?\s+([^\n]+)\n+([^\n]+)\n+(\d{4})',
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': f"{match[0]} in {match[1]}".strip(),
                    'institution': match[2].strip(),
                    'year': match[3].strip()
                })
        
        return education[:3]  # Limit to top 3

    def _extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience with technologies"""
        # Simplified work experience extraction
        return []  # For now, return empty - can be enhanced later

    def _generate_summary(self, skills: List[str], experience: Dict[str, Any], specialization: str) -> str:
        """Generate a professional summary"""
        years = experience.get('years', 0)
        level = experience.get('level', 'junior')
        
        if years > 0:
            exp_text = f"{years}+ years of experience"
        else:
            exp_text = "Experience"
        
        key_skills = skills[:5]  # Top 5 skills
        skills_text = ", ".join(key_skills) if key_skills else "various technologies"
        
        return f"{level.title()} {specialization} professional with {exp_text} in {skills_text}."
