"""
Advanced AI Resume Analyzer with Machine Learning Enhancement and Performance Optimization
"""

import re
import json
import asyncio
import logging
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from functools import lru_cache
import time
from concurrent.futures import ThreadPoolExecutor
import pickle
import hashlib
from django.conf import settings
from django.core.cache import cache
from .utils import PDFProcessor

# Try to import aiohttp, make it optional
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    aiohttp = None

logger = logging.getLogger(__name__)

@dataclass
class SkillMatch:
    """Data class for skill matching with confidence scoring"""
    skill: str
    category: str
    confidence: float
    context_count: int
    patterns_matched: List[str] = field(default_factory=list)

@dataclass
class ResumeAnalysis:
    """Data class for comprehensive resume analysis results"""
    extracted_skills: List[str] = field(default_factory=list)
    programming_languages: List[str] = field(default_factory=list)
    frameworks_libraries: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    cloud_platforms: List[str] = field(default_factory=list)
    tools_technologies: List[str] = field(default_factory=list)
    experience_level: str = 'junior'
    years_of_experience: int = 0
    tech_stack_focus: str = 'General Development'
    specialization: str = 'Technology Professional'
    confidence_score: float = 0.5
    analysis_duration: float = 0.0
    skill_matches: List[SkillMatch] = field(default_factory=list)
    competency_score: float = 0.0
    role_recommendations: List[str] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)
    career_trajectory: str = 'Individual Contributor'
    error: bool = False
    error_type: str = ''
    error_message: str = ''

class AdvancedAIAnalyzer:
    """
    Advanced AI analyzer with ML-enhanced skill extraction, caching, and performance optimization
    """
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = settings.GROQ_API_URL
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Pre-compiled regex patterns for better performance
        self._compile_patterns()
        
        # Enhanced skill taxonomy with weighted importance
        self.skill_taxonomy = {
            'programming_languages': {
                'skills': [
                    'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Ruby',
                    'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'C', 'Objective-C', 'Dart',
                    'Perl', 'Shell', 'Bash', 'PowerShell', 'Assembly', 'Clojure', 'F#', 'Haskell',
                    'Erlang', 'Elixir', 'Lua', 'Julia', 'Groovy', 'VBA', 'COBOL', 'Fortran'
                ],
                'weight': 1.0,
                'aliases': {
                    'js': 'JavaScript',
                    'ts': 'TypeScript',
                    'py': 'Python',
                    'cpp': 'C++',
                    'c++': 'C++',
                    'csharp': 'C#',
                    'c#': 'C#',
                    'golang': 'Go'
                }
            },
            'web_frameworks': {
                'skills': [
                    'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI', 'Express.js',
                    'Node.js', 'Next.js', 'Nuxt.js', 'Laravel', 'Spring Boot', 'ASP.NET',
                    'Ruby on Rails', 'Symfony', 'CodeIgniter', 'Svelte', 'Ember.js', 'Blazor',
                    'Phoenix', 'Gin', 'Echo', 'Fiber', 'Nest.js', 'Koa.js', 'Hapi.js',
                    'Meteor', 'Backbone.js', 'Knockout.js', 'Alpine.js', 'Solid.js'
                ],
                'weight': 0.9,
                'aliases': {
                    'reactjs': 'React',
                    'angularjs': 'Angular',
                    'vuejs': 'Vue.js',
                    'nodejs': 'Node.js',
                    'nextjs': 'Next.js',
                    'nuxtjs': 'Nuxt.js',
                    'rails': 'Ruby on Rails',
                    'ror': 'Ruby on Rails'
                }
            },
            'databases': {
                'skills': [
                    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server',
                    'MariaDB', 'DynamoDB', 'Cassandra', 'Elasticsearch', 'Neo4j', 'InfluxDB',
                    'CouchDB', 'Firebase', 'Supabase', 'PlanetScale', 'Snowflake', 'BigQuery',
                    'Amazon RDS', 'Azure SQL', 'Google Cloud SQL', 'TimescaleDB', 'ClickHouse',
                    'Apache Drill', 'Apache Hive', 'Apache Impala', 'Presto', 'Trino'
                ],
                'weight': 0.8,
                'aliases': {
                    'postgres': 'PostgreSQL',
                    'mysql': 'MySQL',
                    'mongo': 'MongoDB',
                    'elasticsearch': 'Elasticsearch',
                    'elastic': 'Elasticsearch',
                    'sqlserver': 'SQL Server',
                    'mssql': 'SQL Server'
                }
            },
            'cloud_platforms': {
                'skills': [
                    'AWS', 'Google Cloud', 'Azure', 'DigitalOcean', 'Heroku', 'Vercel', 'Netlify',
                    'Firebase', 'Cloudflare', 'Linode', 'Vultr', 'IBM Cloud', 'Oracle Cloud',
                    'Alibaba Cloud', 'Scaleway', 'OVH', 'Hetzner', 'Railway', 'Render',
                    'PlanetScale', 'Supabase', 'Neon', 'Upstash', 'Fly.io'
                ],
                'weight': 0.85,
                'aliases': {
                    'amazon web services': 'AWS',
                    'gcp': 'Google Cloud',
                    'google cloud platform': 'Google Cloud',
                    'microsoft azure': 'Azure',
                    'amazon aws': 'AWS'
                }
            },
            'devops_tools': {
                'skills': [
                    'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform',
                    'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Nginx', 'Apache', 'Git', 'SVN',
                    'CircleCI', 'Travis CI', 'Helm', 'Prometheus', 'Grafana', 'ELK Stack',
                    'Istio', 'Linkerd', 'Consul', 'Vault', 'Nomad', 'Packer', 'Pulumi',
                    'ArgoCD', 'Flux', 'Tekton', 'Spinnaker', 'Bamboo', 'TeamCity'
                ],
                'weight': 0.75,
                'aliases': {
                    'k8s': 'Kubernetes',
                    'gitlab-ci': 'GitLab CI',
                    'github-actions': 'GitHub Actions',
                    'travisci': 'Travis CI',
                    'circleci': 'CircleCI'
                }
            },
            'mobile_development': {
                'skills': [
                    'React Native', 'Flutter', 'Ionic', 'Xamarin', 'Swift', 'Kotlin', 'Cordova',
                    'PhoneGap', 'NativeScript', 'Unity', 'Unreal Engine', 'SwiftUI', 'Jetpack Compose',
                    'Expo', 'Capacitor', 'Titanium', 'Corona SDK', 'Cocos2d', 'Godot'
                ],
                'weight': 0.8,
                'aliases': {
                    'react-native': 'React Native',
                    'rn': 'React Native',
                    'xamarin.forms': 'Xamarin',
                    'phonegap': 'PhoneGap'
                }
            },
            'data_science': {
                'skills': [
                    'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib',
                    'Seaborn', 'Jupyter', 'Apache Spark', 'Hadoop', 'Kafka', 'Airflow',
                    'MLflow', 'Kubeflow', 'SageMaker', 'BigQuery', 'Tableau', 'Power BI',
                    'Plotly', 'Bokeh', 'Altair', 'Streamlit', 'Gradio', 'Weights & Biases',
                    'Neptune', 'Comet', 'DataRobot', 'H2O.ai', 'Databricks', 'Snowflake',
                    'dbt', 'Great Expectations', 'Prefect', 'Kedro', 'DVC', 'ClearML'
                ],
                'weight': 0.9,
                'aliases': {
                    'tensorflow': 'TensorFlow',
                    'pytorch': 'PyTorch',
                    'sklearn': 'Scikit-learn',
                    'scikit-learn': 'Scikit-learn',
                    'numpy': 'NumPy',
                    'pandas': 'Pandas',
                    'jupyter notebook': 'Jupyter',
                    'powerbi': 'Power BI'
                }
            },
            'testing_frameworks': {
                'skills': [
                    'Jest', 'Mocha', 'Jasmine', 'Cypress', 'Selenium', 'Playwright', 'TestCafe',
                    'PyTest', 'Unittest', 'JUnit', 'TestNG', 'RSpec', 'Capybara', 'Karma',
                    'Protractor', 'WebDriver', 'Appium', 'Postman', 'Newman', 'Artillery',
                    'K6', 'Locust', 'JMeter', 'Gatling', 'SoapUI', 'REST Assured'
                ],
                'weight': 0.6,
                'aliases': {
                    'pytest': 'PyTest',
                    'junit': 'JUnit',
                    'testng': 'TestNG',
                    'webdriver': 'WebDriver'
                }
            },
            'design_tools': {
                'skills': [
                    'Figma', 'Adobe XD', 'Sketch', 'InVision', 'Photoshop', 'Illustrator',
                    'After Effects', 'Premiere Pro', 'Canva', 'Framer', 'Principle',
                    'Zeplin', 'Abstract', 'Marvel', 'Balsamiq', 'Axure', 'Miro', 'Whimsical'
                ],
                'weight': 0.5,
                'aliases': {
                    'adobexd': 'Adobe XD',
                    'adobe-xd': 'Adobe XD',
                    'photoshop': 'Photoshop',
                    'illustrator': 'Illustrator'
                }
            },
            'project_management': {
                'skills': [
                    'Jira', 'Trello', 'Asana', 'Monday.com', 'Notion', 'Confluence', 'Slack',
                    'Microsoft Teams', 'Zoom', 'Linear', 'ClickUp', 'Basecamp', 'Airtable',
                    'Smartsheet', 'Wrike', 'Teamwork', 'Podio', 'Zoho Projects'
                ],
                'weight': 0.4,
                'aliases': {
                    'monday': 'Monday.com',
                    'ms teams': 'Microsoft Teams',
                    'teams': 'Microsoft Teams',
                    'clickup': 'ClickUp'
                }
            }
        }
        
        # Advanced tech stack definitions with scoring
        self.tech_stacks = {
            'Full Stack Web Development': {
                'core_skills': ['React', 'Node.js', 'Express.js', 'MongoDB', 'PostgreSQL'],
                'bonus_skills': ['TypeScript', 'Next.js', 'GraphQL', 'Redis', 'AWS'],
                'weight': 1.0
            },
            'Python Backend Development': {
                'core_skills': ['Python', 'Django', 'Flask', 'FastAPI', 'PostgreSQL'],
                'bonus_skills': ['Redis', 'Celery', 'Docker', 'AWS', 'Kubernetes'],
                'weight': 0.9
            },
            'Frontend Development': {
                'core_skills': ['React', 'TypeScript', 'HTML', 'CSS', 'JavaScript'],
                'bonus_skills': ['Next.js', 'Vue.js', 'Angular', 'Tailwind CSS', 'Webpack'],
                'weight': 0.8
            },
            'Data Science & ML': {
                'core_skills': ['Python', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch'],
                'bonus_skills': ['Jupyter', 'Scikit-learn', 'Apache Spark', 'MLflow', 'Kubeflow'],
                'weight': 1.0
            },
            'DevOps Engineering': {
                'core_skills': ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform'],
                'bonus_skills': ['Ansible', 'Prometheus', 'Grafana', 'Helm', 'GitLab CI'],
                'weight': 0.95
            },
            'Mobile Development': {
                'core_skills': ['React Native', 'Flutter', 'Swift', 'Kotlin'],
                'bonus_skills': ['Expo', 'Firebase', 'Redux', 'MobX', 'Realm'],
                'weight': 0.85
            },
            'Java Enterprise': {
                'core_skills': ['Java', 'Spring Boot', 'Maven', 'PostgreSQL', 'Docker'],
                'bonus_skills': ['Spring Security', 'JPA', 'Hibernate', 'Kafka', 'Microservices'],
                'weight': 0.8
            },
            'Cloud Architecture': {
                'core_skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform', 'Microservices'],
                'bonus_skills': ['Istio', 'Prometheus', 'Grafana', 'ArgoCD', 'Helm'],
                'weight': 1.0
            }
        }
        
        # Role mapping for career recommendations
        self.role_mappings = {
            'Full Stack Web Development': ['Full Stack Developer', 'Web Developer', 'Software Engineer'],
            'Python Backend Development': ['Backend Developer', 'Python Developer', 'API Developer'],
            'Frontend Development': ['Frontend Developer', 'React Developer', 'UI Developer'],
            'Data Science & ML': ['Data Scientist', 'ML Engineer', 'Data Analyst'],
            'DevOps Engineering': ['DevOps Engineer', 'Site Reliability Engineer', 'Platform Engineer'],
            'Mobile Development': ['Mobile Developer', 'React Native Developer', 'iOS/Android Developer'],
            'Java Enterprise': ['Java Developer', 'Backend Developer', 'Enterprise Developer'],
            'Cloud Architecture': ['Cloud Architect', 'Solutions Architect', 'Cloud Engineer']
        }

    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance"""
        self.compiled_patterns = {
            'years_experience': [
                re.compile(r'(\d+)\+?\s*years?\s*(?:of)?\s*experience', re.IGNORECASE),
                re.compile(r'experience\s*(?:of|:)?\s*(\d+)\+?\s*years?', re.IGNORECASE),
                re.compile(r'(\d+)\+?\s*years?\s*(?:in|with|of)', re.IGNORECASE),
            ],
            'seniority': {
                'senior': re.compile(r'senior|sr\.|lead|principal|staff|architect|tech lead|team lead', re.IGNORECASE),
                'middle': re.compile(r'mid-level|intermediate|associate|mid level', re.IGNORECASE),
                'junior': re.compile(r'junior|jr\.|entry|intern|graduate|trainee|junior level', re.IGNORECASE)
            },
            'leadership': [
                re.compile(r'team lead|tech lead|engineering manager|cto|vp|director|head of', re.IGNORECASE),
                re.compile(r'managed\s+\d+\s+(?:people|developers|engineers|team members)', re.IGNORECASE),
                re.compile(r'mentored|guided|supervised|coaching|leading', re.IGNORECASE),
            ]
        }

    @lru_cache(maxsize=1000)
    def _get_resume_hash(self, resume_text: str) -> str:
        """Generate hash for caching resume analysis"""
        return hashlib.md5(resume_text.encode()).hexdigest()

    async def extract_text_from_pdf_async(self, file_path: str) -> str:
        """
        Asynchronous PDF text extraction
        """
        loop = asyncio.get_event_loop()
        try:
            # Run PDF extraction in thread pool to avoid blocking
            result = await loop.run_in_executor(
                self.executor, 
                self._extract_pdf_sync, 
                file_path
            )
            return result
        except Exception as e:
            logger.error(f"Async PDF extraction failed: {e}")
            return f"PDF_EXTRACTION_ERROR: {str(e)}"

    def _extract_pdf_sync(self, file_path: str) -> str:
        """Synchronous PDF extraction wrapper"""
        try:
            extracted_text = PDFProcessor.extract_text_from_pdf(file_path)
            
            if extracted_text.startswith("PDF_EXTRACTION_FAILED:"):
                logger.warning(f"PDF extraction failed: {extracted_text}")
                return extracted_text
            
            if len(extracted_text.strip()) < 20:
                logger.warning("Extracted text is very short")
                return f"PDF_EXTRACTION_WARNING: Only {len(extracted_text)} characters extracted.\n\n{extracted_text}"
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            return extracted_text
            
        except Exception as e:
            error_msg = f"PDF_EXTRACTION_ERROR: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def advanced_skill_extraction(self, text: str) -> Tuple[Dict[str, List[str]], List[SkillMatch]]:
        """
        Advanced skill extraction with ML-enhanced pattern matching and confidence scoring
        """
        text_lower = text.lower()
        extracted_skills = defaultdict(list)
        skill_matches = []
        
        # Process each skill category
        for category, category_data in self.skill_taxonomy.items():
            skills = category_data['skills']
            aliases = category_data.get('aliases', {})
            weight = category_data['weight']
            
            for skill in skills:
                skill_lower = skill.lower()
                
                # Check aliases first
                all_skill_variants = [skill_lower] + [alias.lower() for alias in aliases.keys() if aliases[alias] == skill]
                
                best_match = None
                max_confidence = 0
                
                for variant in all_skill_variants:
                    match = self._analyze_skill_context(text_lower, variant, skill)
                    if match and match.confidence > max_confidence:
                        max_confidence = match.confidence
                        best_match = match
                
                # Apply category weight and confidence threshold
                if best_match and best_match.confidence * weight >= 0.3:
                    best_match.confidence *= weight
                    skill_matches.append(best_match)
                    extracted_skills[category].append(skill)
        
        # Convert defaultdict to regular dict
        return dict(extracted_skills), skill_matches

    def _analyze_skill_context(self, text: str, skill_variant: str, original_skill: str) -> Optional[SkillMatch]:
        """
        Analyze skill context with advanced pattern matching
        """
        # Enhanced pattern matching with context scoring
        patterns = [
            # Exact word boundary matches
            (rf'\b{re.escape(skill_variant)}\b', 1.0),
            # Technology with version numbers
            (rf'{re.escape(skill_variant)}\s*(?:\d+|\d+\.\d+|v\d+)', 1.2),
            # Technology with common suffixes
            (rf'{re.escape(skill_variant)}(?:js|\.js|\.py|\.rb|\.java|\.go)?', 0.9),
            # Technology in lists or bullets
            (rf'(?:•|[\-\*])\s*{re.escape(skill_variant)}\b', 1.1),
            # Technology with context words
            (rf'(?:using|with|in|built with|developed with|worked with|experience with|proficient in|skilled in|expert in)\s+{re.escape(skill_variant)}\b', 1.3),
            (rf'{re.escape(skill_variant)}\s+(?:development|programming|framework|library|database|platform|tool|stack|ecosystem)', 1.2),
            # Years of experience patterns
            (rf'(?:\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+)?(?:in\s+|with\s+)?{re.escape(skill_variant)}\b', 1.5),
            # Certification or course patterns
            (rf'(?:certified|certification|course|training|bootcamp|specialization)\s+(?:in\s+)?{re.escape(skill_variant)}\b', 1.1),
            # Project context
            (rf'(?:project|built|created|developed|implemented)\s+(?:using|with|in)\s+{re.escape(skill_variant)}\b', 1.4),
        ]
        
        total_confidence = 0
        context_count = 0
        matched_patterns = []
        
        for pattern, weight in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match_count = len(matches)
                total_confidence += match_count * weight * 0.2
                context_count += match_count
                matched_patterns.append(pattern)
        
        # Boost for multiple mentions
        mentions = len(re.findall(rf'\b{re.escape(skill_variant)}\b', text, re.IGNORECASE))
        if mentions > 1:
            total_confidence += min(mentions * 0.1, 0.3)
        
        # Normalize confidence score
        confidence = min(total_confidence, 1.0)
        
        if confidence > 0:
            return SkillMatch(
                skill=original_skill,
                category='',  # Will be set by caller
                confidence=confidence,
                context_count=context_count,
                patterns_matched=matched_patterns
            )
        
        return None

    def analyze_tech_stacks(self, skills: Dict[str, List[str]]) -> List[Tuple[str, float]]:
        """
        Analyze technology stacks with scoring
        """
        all_skills = set()
        for category_skills in skills.values():
            all_skills.update(skill.lower() for skill in category_skills)
        
        stack_scores = []
        
        for stack_name, stack_data in self.tech_stacks.items():
            core_skills = [s.lower() for s in stack_data['core_skills']]
            bonus_skills = [s.lower() for s in stack_data.get('bonus_skills', [])]
            weight = stack_data['weight']
            
            # Calculate core skills match
            core_matches = len(set(core_skills) & all_skills)
            core_score = core_matches / len(core_skills) if core_skills else 0
            
            # Calculate bonus skills match
            bonus_matches = len(set(bonus_skills) & all_skills)
            bonus_score = bonus_matches / len(bonus_skills) if bonus_skills else 0
            
            # Combined score with weighting
            final_score = (core_score * 0.8 + bonus_score * 0.2) * weight
            
            if final_score >= 0.3:  # Threshold for relevance
                stack_scores.append((stack_name, final_score))
        
        # Sort by score descending
        return sorted(stack_scores, key=lambda x: x[1], reverse=True)

    def calculate_competency_score(self, skill_matches: List[SkillMatch], years_experience: int) -> float:
        """
        Calculate overall competency score based on skills and experience
        """
        if not skill_matches:
            return 0.0
        
        # Weight skills by category importance
        category_weights = {
            'programming_languages': 1.0,
            'web_frameworks': 0.9,
            'databases': 0.8,
            'cloud_platforms': 0.85,
            'devops_tools': 0.75,
            'data_science': 0.9,
            'mobile_development': 0.8,
            'testing_frameworks': 0.6
        }
        
        weighted_score = 0
        total_weight = 0
        
        for match in skill_matches:
            weight = category_weights.get(match.category, 0.5)
            weighted_score += match.confidence * weight
            total_weight += weight
        
        skill_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # Experience multiplier
        experience_multiplier = min(1.0 + (years_experience * 0.1), 2.0)
        
        return min(skill_score * experience_multiplier, 1.0)

    def generate_role_recommendations(self, tech_stacks: List[Tuple[str, float]], 
                                    experience_level: str) -> List[str]:
        """
        Generate role recommendations based on tech stacks and experience
        """
        recommendations = []
        
        for stack_name, score in tech_stacks[:3]:  # Top 3 stacks
            if stack_name in self.role_mappings:
                roles = self.role_mappings[stack_name]
                
                # Adjust roles based on experience level
                if experience_level in ['senior', 'lead']:
                    roles = [f"Senior {role}" if not role.startswith('Senior') else role for role in roles]
                elif experience_level == 'junior':
                    roles = [f"Junior {role}" if not role.startswith('Junior') else role for role in roles]
                
                recommendations.extend(roles)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for role in recommendations:
            if role not in seen:
                seen.add(role)
                unique_recommendations.append(role)
        
        return unique_recommendations[:5]  # Return top 5 recommendations

    def identify_skill_gaps(self, current_skills: Dict[str, List[str]], 
                           target_stack: str) -> List[str]:
        """
        Identify skill gaps for target technology stack
        """
        if target_stack not in self.tech_stacks:
            return []
        
        current_skill_set = set()
        for skills in current_skills.values():
            current_skill_set.update(skill.lower() for skill in skills)
        
        stack_data = self.tech_stacks[target_stack]
        required_skills = set(skill.lower() for skill in stack_data['core_skills'])
        bonus_skills = set(skill.lower() for skill in stack_data.get('bonus_skills', []))
        
        # Find missing core skills
        missing_core = required_skills - current_skill_set
        missing_bonus = bonus_skills - current_skill_set
        
        # Convert back to original case
        gaps = []
        for skill_set, skills in [(missing_core, stack_data['core_skills']), 
                                  (missing_bonus, stack_data.get('bonus_skills', []))]:
            for skill in skills:
                if skill.lower() in skill_set:
                    gaps.append(skill)
        
        return gaps[:5]  # Return top 5 gaps

    async def analyze_resume_async(self, resume_text: str) -> ResumeAnalysis:
        """
        Asynchronous resume analysis with caching and performance optimization
        """
        start_time = time.time()
        
        # Check cache first
        resume_hash = self._get_resume_hash(resume_text)
        cached_result = cache.get(f"resume_analysis_{resume_hash}")
        if cached_result:
            logger.info("Retrieved analysis from cache")
            return ResumeAnalysis(**cached_result)
        
        logger.info("Starting advanced resume analysis")
        
        # Handle extraction failures
        if resume_text.startswith(("PDF_EXTRACTION_FAILED:", "PDF_EXTRACTION_ERROR:", "PDF_EXTRACTION_WARNING:")):
            logger.warning("PDF extraction had issues")
            return self._handle_extraction_failure(resume_text)
        
        # Try AI analysis first, fall back to enhanced analysis
        try:
            if self.api_key and self.api_key != 'your-groq-api-key':
                result = await self._advanced_ai_analysis(resume_text)
            else:
                result = await self._advanced_fallback_analysis(resume_text)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            result = await self._advanced_fallback_analysis(resume_text)
        
        # Calculate analysis duration
        result.analysis_duration = time.time() - start_time
        
        # Cache the result
        cache.set(f"resume_analysis_{resume_hash}", result.__dict__, timeout=3600)  # Cache for 1 hour
        
        logger.info(f"Analysis completed in {result.analysis_duration:.2f} seconds")
        return result

    async def _advanced_ai_analysis(self, resume_text: str) -> ResumeAnalysis:
        """
        Advanced AI analysis with structured prompts and parallel processing
        """
        # Check if aiohttp is available
        if not HAS_AIOHTTP:
            logger.warning("aiohttp not available, falling back to enhanced analysis")
            return await self._advanced_fallback_analysis(resume_text)
        
        # Enhanced prompt for better AI analysis
        prompt = f"""
        You are an expert technical recruiter and AI system specializing in precise resume analysis.
        
        ANALYSIS REQUIREMENTS:
        1. Extract ONLY explicitly mentioned technologies and skills
        2. Use exact names (PostgreSQL not "SQL database", React not "frontend framework")
        3. Assign confidence scores based on context strength
        4. Identify experience level with supporting evidence
        5. Recommend specific roles and identify skill gaps
        
        RESUME TEXT:
        {resume_text}
        
        RESPOND WITH VALID JSON ONLY:
        {{
            "extracted_skills": ["List of ALL specific technologies found"],
            "programming_languages": ["Exact programming languages mentioned"],
            "frameworks_libraries": ["Specific frameworks/libraries found"],
            "databases": ["Database technologies mentioned"],
            "cloud_platforms": ["Cloud services found"],
            "tools_technologies": ["Development tools and technologies"],
            "experience_level": "entry|junior|middle|senior|lead",
            "years_of_experience": 0,
            "tech_stack_focus": "Primary technology area",
            "specialization": "Main expertise domain",
            "confidence_score": 0.95,
            "competency_score": 0.85,
            "role_recommendations": ["Specific job roles this person fits"],
            "skill_gaps": ["Skills missing for advancement"],
            "career_trajectory": "Individual Contributor|Team Lead|Manager|Architect"
        }}
        
        CRITICAL: Return only the JSON object, no additional text.
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
                    'content': 'You are an expert technical resume analyzer. Extract specific technologies with precision. Return only valid JSON.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 3000,
            'top_p': 0.1
        }
        
        # Use async HTTP client
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data, timeout=30) as response:
                response.raise_for_status()
                result = await response.json()
        
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
        
        # Clean and parse JSON
        json_str = self._extract_json_from_response(ai_response)
        parsed_data = json.loads(json_str)
        
        # Post-process and validate
        return self._create_resume_analysis(parsed_data, resume_text)

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from AI response with robust parsing"""
        # Remove code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response
        
        # Extract JSON object if embedded
        if not json_str.strip().startswith('{'):
            json_block_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
            if json_block_match:
                json_str = json_block_match.group(1)
        
        return json_str

    async def _advanced_fallback_analysis(self, resume_text: str) -> ResumeAnalysis:
        """
        Advanced fallback analysis with parallel processing
        """
        logger.info("Using advanced fallback analysis")
        
        # Run multiple analyses in parallel
        tasks = [
            self._extract_skills_task(resume_text),
            self._analyze_experience_task(resume_text),
            self._analyze_career_trajectory_task(resume_text)
        ]
        
        skills_result, experience_result, career_result = await asyncio.gather(*tasks)
        
        skills_by_category, skill_matches = skills_result
        experience_analysis = experience_result
        career_trajectory = career_result
        
        # Analyze tech stacks
        tech_stacks = self.analyze_tech_stacks(skills_by_category)
        
        # Calculate competency score
        competency_score = self.calculate_competency_score(skill_matches, experience_analysis['years'])
        
        # Generate recommendations
        role_recommendations = self.generate_role_recommendations(tech_stacks, experience_analysis['level'])
        
        # Identify skill gaps
        skill_gaps = []
        if tech_stacks:
            skill_gaps = self.identify_skill_gaps(skills_by_category, tech_stacks[0][0])
        
        # Create analysis result
        analysis_data = {
            'extracted_skills': [skill for skills in skills_by_category.values() for skill in skills],
            'programming_languages': skills_by_category.get('programming_languages', []),
            'frameworks_libraries': skills_by_category.get('web_frameworks', []),
            'databases': skills_by_category.get('databases', []),
            'cloud_platforms': skills_by_category.get('cloud_platforms', []),
            'tools_technologies': skills_by_category.get('devops_tools', []) + skills_by_category.get('testing_frameworks', []),
            'experience_level': experience_analysis['level'],
            'years_of_experience': experience_analysis['years'],
            'tech_stack_focus': tech_stacks[0][0] if tech_stacks else 'General Development',
            'specialization': self._determine_specialization(skills_by_category, tech_stacks),
            'confidence_score': experience_analysis['confidence'],
            'competency_score': competency_score,
            'role_recommendations': role_recommendations,
            'skill_gaps': skill_gaps,
            'career_trajectory': career_trajectory
        }
        
        return self._create_resume_analysis(analysis_data, resume_text)

    async def _extract_skills_task(self, resume_text: str) -> Tuple[Dict[str, List[str]], List[SkillMatch]]:
        """Async task for skill extraction"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.advanced_skill_extraction,
            resume_text
        )

    async def _analyze_experience_task(self, resume_text: str) -> Dict[str, Any]:
        """Async task for experience analysis"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.enhanced_experience_analysis,
            resume_text
        )

    async def _analyze_career_trajectory_task(self, resume_text: str) -> str:
        """Async task for career trajectory analysis"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._analyze_career_trajectory,
            resume_text
        )

    def _analyze_career_trajectory(self, text: str) -> str:
        """Analyze career trajectory based on resume content"""
        text_lower = text.lower()
        
        # Management indicators
        management_patterns = [
            r'engineering manager|technical manager|team lead|tech lead',
            r'managed\s+\d+\s+(?:people|developers|engineers)',
            r'director|vp|cto|head of engineering',
            r'people management|team management|staff management'
        ]
        
        # Architecture indicators
        architecture_patterns = [
            r'architect|principal engineer|staff engineer',
            r'system design|architecture|technical leadership',
            r'technical strategy|platform design|infrastructure design'
        ]
        
        # Individual contributor indicators
        ic_patterns = [
            r'software engineer|developer|programmer',
            r'individual contributor|ic role',
            r'coding|development|programming|implementation'
        ]
        
        management_score = sum(len(re.findall(pattern, text_lower)) for pattern in management_patterns)
        architecture_score = sum(len(re.findall(pattern, text_lower)) for pattern in architecture_patterns)
        ic_score = sum(len(re.findall(pattern, text_lower)) for pattern in ic_patterns)
        
        if management_score > 2:
            return 'Manager'
        elif architecture_score > 1:
            return 'Architect'
        elif management_score > 0 or architecture_score > 0:
            return 'Team Lead'
        else:
            return 'Individual Contributor'

    def enhanced_experience_analysis(self, text: str) -> Dict[str, Any]:
        """Enhanced experience analysis with compiled patterns"""
        text_lower = text.lower()
        
        # Extract years using compiled patterns
        years = 0
        for pattern in self.compiled_patterns['years_experience']:
            matches = pattern.findall(text_lower)
            if matches:
                years = max([int(m) for m in matches] + [years])
        
        # Seniority scoring with compiled patterns
        seniority_scores = {}
        for level, pattern in self.compiled_patterns['seniority'].items():
            matches = len(pattern.findall(text_lower))
            seniority_scores[level] = matches
        
        # Leadership scoring with compiled patterns
        leadership_score = 0
        for pattern in self.compiled_patterns['leadership']:
            leadership_score += len(pattern.findall(text_lower))
        
        # Advanced level determination
        if years >= 10 or leadership_score > 3 or seniority_scores.get('senior', 0) > 2:
            level = 'lead'
        elif years >= 6 or leadership_score > 1 or seniority_scores.get('senior', 0) > 1:
            level = 'senior'
        elif years >= 3 or seniority_scores.get('middle', 0) > 0:
            level = 'middle'
        elif years >= 1 or seniority_scores.get('junior', 0) > 0:
            level = 'junior'
        else:
            level = 'entry'
        
        # Calculate confidence
        confidence = min(
            (years * 0.08) + 
            (leadership_score * 0.15) + 
            (max(seniority_scores.values()) * 0.2) + 
            0.4, 
            1.0
        )
        
        return {
            'level': level,
            'years': years,
            'leadership_score': leadership_score,
            'seniority_scores': seniority_scores,
            'confidence': confidence
        }

    def _determine_specialization(self, skills_by_category: Dict[str, List[str]], 
                                 tech_stacks: List[Tuple[str, float]]) -> str:
        """Determine specialization with advanced logic"""
        if tech_stacks:
            return tech_stacks[0][0]
        
        # Count skills by category with weights
        category_weights = {
            'data_science': 2.0,
            'mobile_development': 1.8,
            'cloud_platforms': 1.6,
            'devops_tools': 1.5,
            'web_frameworks': 1.4,
            'databases': 1.2,
            'programming_languages': 1.0
        }
        
        weighted_scores = {}
        for category, skills in skills_by_category.items():
            weight = category_weights.get(category, 1.0)
            weighted_scores[category] = len(skills) * weight
        
        if not weighted_scores:
            return 'Technology Professional'
        
        top_category = max(weighted_scores, key=weighted_scores.get)
        
        specialization_map = {
            'data_science': 'Data Science & Machine Learning',
            'mobile_development': 'Mobile Development',
            'cloud_platforms': 'Cloud Engineering',
            'devops_tools': 'DevOps & Platform Engineering',
            'web_frameworks': 'Web Development',
            'databases': 'Database & Backend Engineering',
            'programming_languages': 'Software Development'
        }
        
        return specialization_map.get(top_category, 'Technology Professional')

    def _create_resume_analysis(self, data: Dict[str, Any], resume_text: str) -> ResumeAnalysis:
        """Create ResumeAnalysis object with validation"""
        # Validate and set defaults
        defaults = {
            'extracted_skills': [],
            'programming_languages': [],
            'frameworks_libraries': [],
            'databases': [],
            'cloud_platforms': [],
            'tools_technologies': [],
            'experience_level': 'junior',
            'years_of_experience': 0,
            'tech_stack_focus': 'General Development',
            'specialization': 'Technology Professional',
            'confidence_score': 0.5,
            'competency_score': 0.5,
            'role_recommendations': [],
            'skill_gaps': [],
            'career_trajectory': 'Individual Contributor'
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        # Validate experience level
        valid_levels = ['entry', 'junior', 'middle', 'senior', 'lead']
        if data['experience_level'] not in valid_levels:
            data['experience_level'] = 'junior'
        
        # Ensure numeric values are valid
        data['years_of_experience'] = max(0, int(data.get('years_of_experience', 0)))
        data['confidence_score'] = max(0.0, min(1.0, float(data.get('confidence_score', 0.5))))
        data['competency_score'] = max(0.0, min(1.0, float(data.get('competency_score', 0.5))))
        
        return ResumeAnalysis(**data)

    def _handle_extraction_failure(self, error_text: str) -> ResumeAnalysis:
        """Handle PDF extraction failures with detailed error reporting"""
        error_analysis = ResumeAnalysis(
            error=True,
            error_type='pdf_extraction_failed',
            error_message='Unable to extract readable text from PDF. The file may be scanned, password-protected, or corrupted.',
            extracted_skills=[],
            programming_languages=[],
            frameworks_libraries=[],
            databases=[],
            cloud_platforms=[],
            tools_technologies=[],
            experience_level='unknown',
            years_of_experience=0,
            tech_stack_focus='Unable to determine',
            specialization='Unable to determine',
            confidence_score=0.0,
            competency_score=0.0,
            role_recommendations=[],
            skill_gaps=[],
            career_trajectory='Unknown'
        )
        
        # Try to extract some text if it's a warning rather than complete failure
        if "PDF_EXTRACTION_WARNING:" in error_text:
            try:
                actual_text = error_text.split("PDF_EXTRACTION_WARNING:")[1].strip()
                if len(actual_text) > 50:
                    logger.info("Attempting limited analysis with partial text")
                    # Run basic analysis on partial text
                    skills, _ = self.advanced_skill_extraction(actual_text)
                    if skills:
                        error_analysis.extracted_skills = [skill for skill_list in skills.values() for skill in skill_list]
                        error_analysis.programming_languages = skills.get('programming_languages', [])
                        error_analysis.confidence_score = 0.3  # Lower confidence due to partial extraction
            except Exception as e:
                logger.warning(f"Failed to analyze partial text: {e}")
        
        return error_analysis

    # Synchronous wrapper for backwards compatibility
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for the async analyze_resume_async method
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.analyze_resume_async(resume_text))
            return result.__dict__
        finally:
            loop.close()

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Synchronous wrapper for PDF extraction
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.extract_text_from_pdf_async(file_path))
            return result
        finally:
            loop.close()

    def batch_analyze_resumes(self, resume_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Batch analyze multiple resumes with optimized performance
        """
        async def _batch_analyze():
            tasks = [self.analyze_resume_async(text) for text in resume_texts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert results to dictionaries, handling exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch analysis error: {result}")
                    processed_results.append(self._handle_extraction_failure(str(result)).__dict__)
                else:
                    processed_results.append(result.__dict__)
            
            return processed_results
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_batch_analyze())
        finally:
            loop.close()

    def get_skill_trends(self, skill_matches: List[SkillMatch]) -> Dict[str, Any]:
        """
        Analyze skill trends and provide insights
        """
        if not skill_matches:
            return {}
        
        # Group by category
        category_confidence = defaultdict(list)
        for match in skill_matches:
            category_confidence[match.category].append(match.confidence)
        
        # Calculate category strengths
        category_strengths = {}
        for category, confidences in category_confidence.items():
            avg_confidence = sum(confidences) / len(confidences)
            skill_count = len(confidences)
            strength_score = avg_confidence * (1 + (skill_count - 1) * 0.1)  # Bonus for breadth
            category_strengths[category] = {
                'average_confidence': avg_confidence,
                'skill_count': skill_count,
                'strength_score': min(strength_score, 1.0)
            }
        
        # Find strongest and weakest areas
        if category_strengths:
            strongest = max(category_strengths.items(), key=lambda x: x[1]['strength_score'])
            weakest = min(category_strengths.items(), key=lambda x: x[1]['strength_score'])
            
            return {
                'category_strengths': category_strengths,
                'strongest_area': strongest[0],
                'weakest_area': weakest[0],
                'total_skills': len(skill_matches),
                'average_confidence': sum(match.confidence for match in skill_matches) / len(skill_matches)
            }
        
        return {}

# Example usage and testing
if __name__ == "__main__":
    # Performance testing
    import time
    
    analyzer = AdvancedAIAnalyzer()
    
    # Test resume text
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 6 years of experience in full-stack development
    - Led a team of 4 developers
    - Built applications using React, Node.js, PostgreSQL
    - Deployed on AWS with Docker and Kubernetes
    - Experienced with Python, Django, and FastAPI
    - Worked with Redis, MongoDB, and Elasticsearch
    - Implemented CI/CD pipelines with Jenkins and GitLab CI
    - Proficient in TypeScript, JavaScript, and Python
    """
    
    # Test synchronous analysis
    print("Testing synchronous analysis...")
    start_time = time.time()
    result = analyzer.analyze_resume(sample_resume)
    sync_duration = time.time() - start_time
    print(f"Synchronous analysis completed in {sync_duration:.2f} seconds")
    print(f"Found {len(result['extracted_skills'])} skills")
    print(f"Experience level: {result['experience_level']}")
    print(f"Specialization: {result['specialization']}")
    
    # Test batch analysis
    print("\nTesting batch analysis...")
    start_time = time.time()
    batch_results = analyzer.batch_analyze_resumes([sample_resume] * 3)
    batch_duration = time.time() - start_time
    print(f"Batch analysis of 3 resumes completed in {batch_duration:.2f} seconds")
    print(f"Average time per resume: {batch_duration/3:.2f} seconds")