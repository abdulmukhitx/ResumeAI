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
        """
        Enhanced PDF text extraction with robust error handling
        """
        try:
            extracted_text = PDFProcessor.extract_text_from_pdf(file_path)
            
            # Check if extraction failed
            if extracted_text.startswith("PDF_EXTRACTION_FAILED:"):
                logger.warning(f"PDF extraction failed: {extracted_text}")
                # Return the error message for better user feedback
                return extracted_text
            
            # Validate extracted text quality
            if len(extracted_text.strip()) < 20:
                logger.warning("Extracted text is very short - possible extraction issue")
                return f"PDF_EXTRACTION_WARNING: Only {len(extracted_text)} characters extracted. Text may be incomplete.\n\n{extracted_text}"
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            return extracted_text
            
        except Exception as e:
            error_msg = f"PDF_EXTRACTION_ERROR: Unexpected error during PDF processing: {str(e)}"
            logger.error(error_msg)
            return error_msg

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
        Enhanced resume analysis with improved AI prompts and robust fallback
        """
        logger.info("Starting enhanced resume analysis")
        
        # Check if text extraction failed
        if resume_text.startswith(("PDF_EXTRACTION_FAILED:", "PDF_EXTRACTION_ERROR:", "PDF_EXTRACTION_WARNING:")):
            logger.warning("PDF extraction had issues, using limited analysis")
            return self._handle_extraction_failure(resume_text)
        
        # First, try enhanced AI analysis
        if self.api_key and self.api_key != 'your-groq-api-key':
            try:
                return self._enhanced_ai_analysis(resume_text)
            except Exception as e:
                logger.warning(f"AI analysis failed, using enhanced fallback: {e}")
        
        # Use enhanced fallback analysis
        return self._enhanced_fallback_analysis(resume_text)
    
    def _handle_extraction_failure(self, error_text: str) -> Dict[str, Any]:
        """
        Handle cases where PDF extraction failed
        """
        # Extract any partial text that might be available
        if "PDF_EXTRACTION_WARNING:" in error_text:
            # Some text was extracted, try to analyze it
            actual_text = error_text.split("PDF_EXTRACTION_WARNING:")[1].strip()
            if len(actual_text) > 50:
                logger.info("Attempting analysis with partially extracted text")
                return self._enhanced_fallback_analysis(actual_text)
        
        # Return error analysis result
        return {
            'error': True,
            'error_type': 'pdf_extraction_failed',
            'error_message': 'Unable to extract readable text from PDF. The file may be scanned, password-protected, or corrupted.',
            'suggestions': [
                'Ensure the PDF contains selectable text (not just scanned images)',
                'Check if the PDF is password-protected or corrupted',
                'Try converting the PDF to a different format',
                'If the resume is scanned, consider using a PDF with OCR text layer'
            ],
            'extracted_skills': [],
            'programming_languages': [],
            'frameworks_libraries': [],
            'databases': [],
            'cloud_platforms': [],
            'tools_technologies': [],
            'experience_level': 'unknown',
            'years_of_experience': 0,
            'tech_stack_focus': 'Unable to determine',
            'specialization': 'Unable to determine',
            'confidence_score': 0.0,
            'analysis_status': 'failed_pdf_extraction'
        }

    def _enhanced_ai_analysis(self, resume_text: str) -> Dict[str, Any]:
        """
        Enhanced AI analysis with better prompts for specific skill extraction
        """
        prompt = f"""
        You are an expert technical recruiter analyzing resumes. Extract SPECIFIC, CONCRETE skills and technologies.

        CRITICAL RULES:
        1. Extract ONLY technologies explicitly mentioned
        2. Use EXACT names (e.g., "PostgreSQL", not "SQL database")
        3. Don't infer skills not clearly stated
        4. Focus on specific frameworks, tools, and technologies

        Resume Text:
        {resume_text}

        Return a JSON object with this structure:
        {{
            "extracted_skills": ["List of ALL specific technologies mentioned"],
            "programming_languages": ["Python", "JavaScript", "Java", etc.],
            "frameworks_libraries": ["Django", "React", "Angular", etc.],
            "databases": ["PostgreSQL", "MongoDB", "Redis", etc.],
            "cloud_platforms": ["AWS", "Google Cloud", "Azure", etc.],
            "tools_technologies": ["Docker", "Kubernetes", "Git", etc.],
            "experience_level": "entry/junior/middle/senior/lead",
            "years_of_experience": 0,
            "tech_stack_focus": "Primary technology area",
            "specialization": "Main expertise area",
            "confidence_score": 0.95
        }}

        Return ONLY the JSON object.
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'llama3-70b-8192',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert technical resume analyzer. Extract specific technologies with high precision. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 2000
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
            'confidence_score': experience_analysis['confidence']
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
                if field.endswith('s') and field != 'years_of_experience':
                    data[field] = []
                elif field == 'years_of_experience':
                    data[field] = 0
                elif field == 'confidence_score':
                    data[field] = 0.5
                else:
                    data[field] = 'unknown'
        
        # Validate experience level
        valid_levels = ['entry', 'junior', 'middle', 'senior', 'lead']
        if data.get('experience_level') not in valid_levels:
            data['experience_level'] = 'junior'
        
        # Ensure confidence score is between 0 and 1
        confidence = data.get('confidence_score', 0.5)
        data['confidence_score'] = max(0.0, min(1.0, float(confidence)))
        
        return data
