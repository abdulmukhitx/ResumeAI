"""
Advanced AI-Powered Job Matching System with Machine Learning and Semantic Analysis
"""

import re
import logging
import asyncio
import json
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from django.apps import apps
from django.db import transaction, models
from django.core.cache import cache
from django.utils import timezone
from .enhanced_analyzer import AdvancedAIAnalyzer

logger = logging.getLogger(__name__)

# Dynamically load models
Job = apps.get_model('jobs', 'Job')
JobMatch = apps.get_model('jobs', 'JobMatch')

@dataclass
class SkillMatch:
    """Data class for skill matching details"""
    skill: str
    confidence: float
    skill_type: str
    frequency_in_jobs: int
    market_demand: float
    learning_priority: int

@dataclass
class MatchInsights:
    """Data class for match insights and recommendations"""
    skill_gaps: List[SkillMatch]
    career_growth_potential: float
    salary_range_match: Tuple[float, float]
    learning_path: List[str]
    alternative_roles: List[str]
    market_trends: Dict[str, float]

class AdvancedJobMatcher:
    """
    Advanced AI-powered job matcher with ML algorithms and semantic analysis
    """
    
    def __init__(self, user, resume):
        self.user = user
        self.resume = resume
        self.analyzer = AdvancedAIAnalyzer()
        self.cache_timeout = 3600  # 1 hour cache
        
        # Initialize ML components
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        self.scaler = StandardScaler()
        
        # Advanced skill categorization with market weights
        self.skill_taxonomy = {
            'core_programming': {
                'weight': 1.0,
                'skills': ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'TypeScript', 'Swift', 'Kotlin'],
                'demand_multiplier': 1.2
            },
            'web_frameworks': {
                'weight': 0.95,
                'skills': ['React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Express.js', 'Spring', 'ASP.NET'],
                'demand_multiplier': 1.15
            },
            'data_technologies': {
                'weight': 0.9,
                'skills': ['pandas', 'numpy', 'scikit-learn', 'TensorFlow', 'PyTorch', 'Keras', 'Apache Spark', 'Hadoop'],
                'demand_multiplier': 1.3
            },
            'cloud_platforms': {
                'weight': 0.85,
                'skills': ['AWS', 'Azure', 'Google Cloud', 'Kubernetes', 'Docker', 'Terraform', 'Jenkins', 'GitLab CI'],
                'demand_multiplier': 1.25
            },
            'databases': {
                'weight': 0.8,
                'skills': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB', 'Oracle', 'SQLite'],
                'demand_multiplier': 1.1
            },
            'mobile_development': {
                'weight': 0.75,
                'skills': ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Xamarin', 'Ionic', 'Unity'],
                'demand_multiplier': 1.1
            },
            'devops_tools': {
                'weight': 0.85,
                'skills': ['Git', 'GitHub', 'GitLab', 'Jira', 'Confluence', 'Ansible', 'Puppet', 'Chef'],
                'demand_multiplier': 1.2
            },
            'emerging_tech': {
                'weight': 0.95,
                'skills': ['Blockchain', 'Web3', 'AI/ML', 'IoT', 'AR/VR', 'GraphQL', 'Serverless', 'Microservices'],
                'demand_multiplier': 1.4
            }
        }
        
        # Advanced job archetypes with skill requirements and career paths
        self.job_archetypes = {
            'senior_fullstack_engineer': {
                'required_skills': ['JavaScript', 'React', 'Node.js', 'Python', 'SQL'],
                'preferred_skills': ['TypeScript', 'AWS', 'Docker', 'GraphQL', 'Redux'],
                'experience_range': (3, 8),
                'salary_range': (80000, 150000),
                'growth_potential': 0.85,
                'keywords': ['senior full stack', 'full stack engineer', 'fullstack developer'],
                'career_path': ['Junior Developer', 'Mid-level Developer', 'Senior Developer', 'Tech Lead', 'Engineering Manager']
            },
            'ml_engineer': {
                'required_skills': ['Python', 'TensorFlow', 'PyTorch', 'scikit-learn', 'pandas'],
                'preferred_skills': ['AWS', 'Docker', 'Kubernetes', 'MLOps', 'Apache Spark'],
                'experience_range': (2, 6),
                'salary_range': (90000, 170000),
                'growth_potential': 0.95,
                'keywords': ['machine learning engineer', 'ml engineer', 'ai engineer'],
                'career_path': ['Data Analyst', 'ML Engineer', 'Senior ML Engineer', 'ML Architect', 'Head of AI']
            },
            'cloud_architect': {
                'required_skills': ['AWS', 'Azure', 'Kubernetes', 'Docker', 'Terraform'],
                'preferred_skills': ['Python', 'Go', 'Jenkins', 'Ansible', 'Security'],
                'experience_range': (5, 12),
                'salary_range': (120000, 200000),
                'growth_potential': 0.8,
                'keywords': ['cloud architect', 'solution architect', 'infrastructure architect'],
                'career_path': ['DevOps Engineer', 'Cloud Engineer', 'Cloud Architect', 'Principal Architect', 'CTO']
            },
            'data_scientist': {
                'required_skills': ['Python', 'R', 'SQL', 'pandas', 'numpy'],
                'preferred_skills': ['TensorFlow', 'PyTorch', 'Tableau', 'Power BI', 'Apache Spark'],
                'experience_range': (1, 5),
                'salary_range': (70000, 140000),
                'growth_potential': 0.9,
                'keywords': ['data scientist', 'data analyst', 'research scientist'],
                'career_path': ['Data Analyst', 'Data Scientist', 'Senior Data Scientist', 'Lead Data Scientist', 'Chief Data Officer']
            },
            'frontend_specialist': {
                'required_skills': ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript'],
                'preferred_skills': ['Next.js', 'Vue.js', 'Sass', 'Webpack', 'Jest'],
                'experience_range': (2, 7),
                'salary_range': (65000, 130000),
                'growth_potential': 0.75,
                'keywords': ['frontend developer', 'ui developer', 'react developer'],
                'career_path': ['Junior Frontend', 'Frontend Developer', 'Senior Frontend', 'Frontend Architect', 'Head of Frontend']
            },
            'backend_specialist': {
                'required_skills': ['Python', 'Java', 'SQL', 'REST API', 'Microservices'],
                'preferred_skills': ['Django', 'Spring', 'PostgreSQL', 'Redis', 'Apache Kafka'],
                'experience_range': (2, 8),
                'salary_range': (70000, 140000),
                'growth_potential': 0.8,
                'keywords': ['backend developer', 'api developer', 'server developer'],
                'career_path': ['Junior Backend', 'Backend Developer', 'Senior Backend', 'Backend Architect', 'Principal Engineer']
            }
        }

    async def analyze_resume_advanced(self) -> Dict[str, Any]:
        """
        Advanced resume analysis with caching and ML-based skill extraction
        """
        cache_key = f"resume_analysis_{self.resume.id}_{self.resume.updated_at.timestamp()}"
        cached_analysis = cache.get(cache_key)
        
        if cached_analysis:
            logger.info("Using cached resume analysis")
            return cached_analysis
        
        try:
            # Extract and process resume text
            raw_text = await self._extract_resume_text()
            if not raw_text:
                return {}
            
            # Parallel processing for different analysis components
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Submit all analysis tasks
                basic_analysis_future = executor.submit(self.analyzer.analyze_resume, raw_text)
                skills_future = executor.submit(self._extract_skills_with_confidence, raw_text)
                experience_future = executor.submit(self._analyze_experience_depth, raw_text)
                domain_future = executor.submit(self._identify_domain_expertise, raw_text)
                
                # Collect results
                basic_analysis = basic_analysis_future.result()
                skills_with_confidence = skills_future.result()
                experience_analysis = experience_future.result()
                domain_expertise = domain_future.result()
            
            # Merge all analysis results
            enhanced_analysis = {
                **basic_analysis,
                'skills_with_confidence': skills_with_confidence,
                'experience_depth': experience_analysis,
                'domain_expertise': domain_expertise,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_version': 'advanced_v2.0'
            }
            
            # Cache the results
            cache.set(cache_key, enhanced_analysis, self.cache_timeout)
            
            # Update resume record
            await self._update_resume_record(enhanced_analysis)
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in advanced resume analysis: {e}")
            return {}

    async def _extract_resume_text(self) -> str:
        """Extract text from resume with better error handling"""
        try:
            if hasattr(self.resume, 'raw_text') and self.resume.raw_text:
                return self.resume.raw_text
            
            if hasattr(self.resume, 'file') and self.resume.file:
                return await asyncio.to_thread(
                    self.analyzer.extract_text_from_pdf, 
                    self.resume.file.path
                )
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting resume text: {e}")
            return ""

    def _extract_skills_with_confidence(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract skills with confidence scores and categorization
        """
        skills_by_category = defaultdict(list)
        text_lower = text.lower()
        
        for category, category_data in self.skill_taxonomy.items():
            for skill in category_data['skills']:
                skill_lower = skill.lower()
                confidence = self._calculate_skill_confidence(text_lower, skill_lower)
                
                if confidence > 0.3:  # Threshold for inclusion
                    skills_by_category[category].append({
                        'skill': skill,
                        'confidence': confidence,
                        'demand_multiplier': category_data['demand_multiplier'],
                        'category_weight': category_data['weight']
                    })
        
        return dict(skills_by_category)

    def _calculate_skill_confidence(self, text: str, skill: str) -> float:
        """
        Calculate confidence score for a skill based on context and frequency
        """
        confidence = 0.0
        
        # Direct mentions
        direct_matches = len(re.findall(rf'\b{re.escape(skill)}\b', text))
        confidence += min(direct_matches * 0.3, 1.0)
        
        # Context-based matches
        context_patterns = [
            rf'(?:experience|expertise|proficient|skilled|worked)\s+(?:with|in)\s+{re.escape(skill)}',
            rf'{re.escape(skill)}\s+(?:development|programming|experience|expertise)',
            rf'(?:using|utilized|implemented|developed)\s+{re.escape(skill)}',
            rf'{re.escape(skill)}\s+(?:projects|applications|systems)'
        ]
        
        for pattern in context_patterns:
            if re.search(pattern, text):
                confidence += 0.4
                break
        
        # Years of experience mentions
        years_pattern = rf'(\d+)\s*(?:\+|\-)?(?:\s*years?)\s+(?:of\s+)?(?:experience\s+)?(?:with\s+)?{re.escape(skill)}'
        years_matches = re.findall(years_pattern, text)
        if years_matches:
            max_years = max(int(year) for year in years_matches)
            confidence += min(max_years * 0.1, 0.5)
        
        # Project mentions
        project_pattern = rf'(?:project|application|system|platform).*{re.escape(skill)}'
        if re.search(project_pattern, text):
            confidence += 0.2
        
        return min(confidence, 1.0)

    def _analyze_experience_depth(self, text: str) -> Dict[str, Any]:
        """
        Analyze experience depth and career progression
        """
        # Extract years of experience
        years_patterns = [
            r'(\d+)\s*(?:\+|\-)?(?:\s*years?)\s+(?:of\s+)?(?:experience|exp)',
            r'(?:over|more than|above)\s+(\d+)\s+years?',
            r'(\d+)\s*(?:\+|\-)\s*years?'
        ]
        
        all_years = []
        for pattern in years_patterns:
            matches = re.findall(pattern, text.lower())
            all_years.extend([int(year) for year in matches])
        
        # Extract role progression
        role_levels = {
            'junior': ['junior', 'entry', 'associate', 'intern'],
            'mid': ['developer', 'engineer', 'analyst', 'consultant'],
            'senior': ['senior', 'lead', 'principal', 'staff'],
            'executive': ['manager', 'director', 'head', 'chief', 'vp']
        }
        
        role_progression = []
        for level, keywords in role_levels.items():
            for keyword in keywords:
                if keyword in text.lower():
                    role_progression.append(level)
                    break
        
        return {
            'total_years': max(all_years) if all_years else 0,
            'experience_range': (min(all_years), max(all_years)) if all_years else (0, 0),
            'role_progression': list(set(role_progression)),
            'leadership_indicators': self._extract_leadership_indicators(text),
            'project_scale': self._assess_project_scale(text)
        }

    def _extract_leadership_indicators(self, text: str) -> List[str]:
        """Extract leadership and management indicators"""
        leadership_patterns = [
            r'(?:led|managed|supervised|mentored|guided)\s+(?:team|developers|engineers)',
            r'(?:technical|team|project)\s+lead',
            r'(?:managed|oversaw|coordinated)\s+(?:projects|initiatives)',
            r'(?:mentored|trained|coached)\s+(?:junior|new|team members)'
        ]
        
        indicators = []
        for pattern in leadership_patterns:
            if re.search(pattern, text.lower()):
                indicators.append(pattern.replace(r'\s+', ' ').replace('(?:', '').replace(')', ''))
        
        return indicators

    def _assess_project_scale(self, text: str) -> Dict[str, Any]:
        """Assess the scale and complexity of projects"""
        scale_indicators = {
            'team_size': re.findall(r'team\s+of\s+(\d+)', text.lower()),
            'user_base': re.findall(r'(\d+(?:k|m|million|thousand))\s+users?', text.lower()),
            'revenue_impact': re.findall(r'\$(\d+(?:k|m|million|thousand))', text.lower()),
            'complexity_keywords': ['microservices', 'distributed', 'scalable', 'high-availability', 'enterprise']
        }
        
        complexity_score = 0
        for keyword in scale_indicators['complexity_keywords']:
            if keyword in text.lower():
                complexity_score += 1
        
        return {
            'team_sizes': [int(size) for size in scale_indicators['team_size']],
            'user_base_mentions': scale_indicators['user_base'],
            'revenue_mentions': scale_indicators['revenue_impact'],
            'complexity_score': complexity_score
        }

    def _identify_domain_expertise(self, text: str) -> Dict[str, float]:
        """Identify domain expertise with confidence scores"""
        domains = {
            'fintech': ['financial', 'banking', 'payment', 'trading', 'investment', 'cryptocurrency'],
            'healthcare': ['medical', 'health', 'clinical', 'pharmaceutical', 'biotech'],
            'ecommerce': ['retail', 'marketplace', 'shopping', 'commerce', 'payment'],
            'education': ['educational', 'learning', 'academic', 'university', 'school'],
            'gaming': ['game', 'gaming', 'entertainment', 'graphics', 'simulation'],
            'enterprise': ['enterprise', 'business', 'corporate', 'saas', 'b2b'],
            'startup': ['startup', 'early-stage', 'mvp', 'rapid growth', 'agile']
        }
        
        domain_scores = {}
        text_lower = text.lower()
        
        for domain, keywords in domains.items():
            score = 0
            for keyword in keywords:
                score += len(re.findall(rf'\b{re.escape(keyword)}\b', text_lower))
            
            if score > 0:
                domain_scores[domain] = min(score / 10, 1.0)  # Normalize to 0-1
        
        return domain_scores

    async def calculate_advanced_match_score(self, job: Any, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate advanced match score using ML algorithms and semantic analysis
        """
        try:
            # Extract job information
            job_text = self._extract_job_text(job)
            job_archetype = self._identify_job_archetype(job_text)
            
            # Multi-dimensional scoring
            scores = await self._calculate_multi_dimensional_scores(job, job_text, job_archetype, resume_analysis)
            
            # ML-based semantic similarity
            semantic_score = await self._calculate_semantic_similarity(job_text, resume_analysis)
            
            # Market alignment score
            market_score = self._calculate_market_alignment(job_archetype, resume_analysis)
            
            # Combine all scores with weights
            final_score = (
                scores['skill_match'] * 0.35 +
                scores['experience_match'] * 0.25 +
                semantic_score * 0.20 +
                market_score * 0.15 +
                scores['domain_match'] * 0.05
            )
            
            # Generate insights and recommendations
            insights = self._generate_match_insights(job, job_archetype, resume_analysis, scores)
            
            return {
                'match_score': min(max(final_score, 0), 100),
                'score_breakdown': {
                    'skill_alignment': scores['skill_match'],
                    'experience_fit': scores['experience_match'],
                    'semantic_similarity': semantic_score,
                    'market_alignment': market_score,
                    'domain_expertise': scores['domain_match']
                },
                'match_insights': insights,
                'archetype_match': job_archetype,
                'confidence_level': self._calculate_confidence_level(scores, semantic_score, market_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating advanced match score: {e}")
            return {'match_score': 0, 'error': str(e)}

    def _extract_job_text(self, job: Any) -> str:
        """Extract and clean job text"""
        components = []
        
        if hasattr(job, 'title') and job.title:
            components.append(job.title)
        if hasattr(job, 'description') and job.description:
            components.append(job.description)
        if hasattr(job, 'requirements') and job.requirements:
            components.append(job.requirements)
        if hasattr(job, 'responsibilities') and job.responsibilities:
            components.append(job.responsibilities)
            
        return ' '.join(components).lower()

    def _identify_job_archetype(self, job_text: str) -> str:
        """Identify job archetype using advanced pattern matching"""
        archetype_scores = {}
        
        for archetype, config in self.job_archetypes.items():
            score = 0
            
            # Keyword matching
            for keyword in config['keywords']:
                if keyword in job_text:
                    score += 3
            
            # Required skills matching
            for skill in config['required_skills']:
                if skill.lower() in job_text:
                    score += 2
            
            # Preferred skills matching
            for skill in config['preferred_skills']:
                if skill.lower() in job_text:
                    score += 1
            
            if score > 0:
                archetype_scores[archetype] = score
        
        if archetype_scores:
            return max(archetype_scores, key=archetype_scores.get)
        
        return 'general_software_engineer'

    async def _calculate_multi_dimensional_scores(self, job: Any, job_text: str, archetype: str, resume_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores across multiple dimensions"""
        
        # Skill matching with confidence weights
        skill_score = self._calculate_weighted_skill_match(job_text, resume_analysis)
        
        # Experience matching
        experience_score = self._calculate_experience_match(job_text, archetype, resume_analysis)
        
        # Domain expertise matching
        domain_score = self._calculate_domain_match(job_text, resume_analysis)
        
        return {
            'skill_match': skill_score,
            'experience_match': experience_score,
            'domain_match': domain_score
        }

    def _calculate_weighted_skill_match(self, job_text: str, resume_analysis: Dict[str, Any]) -> float:
        """Calculate skill match with confidence and market weights"""
        skills_with_confidence = resume_analysis.get('skills_with_confidence', {})
        total_score = 0
        total_weight = 0
        
        for category, skills in skills_with_confidence.items():
            category_weight = self.skill_taxonomy.get(category, {}).get('weight', 0.5)
            
            for skill_data in skills:
                skill = skill_data['skill'].lower()
                confidence = skill_data['confidence']
                demand_multiplier = skill_data['demand_multiplier']
                
                # Check if skill is mentioned in job
                if skill in job_text:
                    skill_weight = category_weight * confidence * demand_multiplier
                    total_score += skill_weight * 100
                    total_weight += skill_weight
        
        return (total_score / total_weight) if total_weight > 0 else 0

    def _calculate_experience_match(self, job_text: str, archetype: str, resume_analysis: Dict[str, Any]) -> float:
        """Calculate experience match with role progression analysis"""
        experience_depth = resume_analysis.get('experience_depth', {})
        user_years = experience_depth.get('total_years', 0)
        role_progression = experience_depth.get('role_progression', [])
        
        # Get archetype requirements
        archetype_config = self.job_archetypes.get(archetype, {})
        required_range = archetype_config.get('experience_range', (0, 10))
        
        # Years match
        years_score = 0
        min_years, max_years = required_range
        
        if min_years <= user_years <= max_years:
            years_score = 100
        elif user_years > max_years:
            # Overqualified but still good
            years_score = max(80 - (user_years - max_years) * 5, 60)
        elif user_years < min_years:
            # Underqualified
            years_score = max(user_years / min_years * 70, 20)
        
        # Role progression match
        progression_score = 0
        if 'senior' in role_progression and 'senior' in job_text:
            progression_score = 100
        elif 'senior' not in role_progression and 'junior' in job_text:
            progression_score = 90
        elif role_progression:
            progression_score = 70
        else:
            progression_score = 40
        
        return (years_score * 0.6 + progression_score * 0.4)

    def _calculate_domain_match(self, job_text: str, resume_analysis: Dict[str, Any]) -> float:
        """Calculate domain expertise match"""
        domain_expertise = resume_analysis.get('domain_expertise', {})
        
        max_score = 0
        for domain, confidence in domain_expertise.items():
            # Check if domain keywords appear in job
            domain_keywords = {
                'fintech': ['financial', 'banking', 'payment', 'trading'],
                'healthcare': ['medical', 'health', 'clinical'],
                'ecommerce': ['retail', 'marketplace', 'commerce'],
                'education': ['educational', 'learning', 'academic'],
                'gaming': ['game', 'gaming', 'entertainment'],
                'enterprise': ['enterprise', 'business', 'corporate'],
                'startup': ['startup', 'early-stage', 'mvp']
            }.get(domain, [])
            
            domain_match = any(keyword in job_text for keyword in domain_keywords)
            if domain_match:
                max_score = max(max_score, confidence * 100)
        
        return max_score

    async def _calculate_semantic_similarity(self, job_text: str, resume_analysis: Dict[str, Any]) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        try:
            # Get resume text
            resume_text = resume_analysis.get('raw_text', '')
            if not resume_text:
                return 0
            
            # Vectorize texts
            documents = [job_text, resume_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            semantic_score = similarity_matrix[0][1] * 100  # Convert to percentage
            
            return semantic_score
            
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0

    def _calculate_market_alignment(self, archetype: str, resume_analysis: Dict[str, Any]) -> float:
        """Calculate alignment with current market trends"""
        archetype_config = self.job_archetypes.get(archetype, {})
        growth_potential = archetype_config.get('growth_potential', 0.5)
        
        # Factor in emerging technologies
        skills_with_confidence = resume_analysis.get('skills_with_confidence', {})
        emerging_tech_score = 0
        
        if 'emerging_tech' in skills_with_confidence:
            emerging_skills = skills_with_confidence['emerging_tech']
            for skill_data in emerging_skills:
                emerging_tech_score += skill_data['confidence'] * skill_data['demand_multiplier']
        
        # Normalize emerging tech score
        emerging_tech_score = min(emerging_tech_score * 20, 50)  # Cap at 50%
        
        return (growth_potential * 50 + emerging_tech_score)

    def _generate_match_insights(self, job: Any, archetype: str, resume_analysis: Dict[str, Any], scores: Dict[str, float]) -> MatchInsights:
        """Generate detailed insights and recommendations"""
        
        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(job, archetype, resume_analysis)
        
        # Calculate career growth potential
        archetype_config = self.job_archetypes.get(archetype, {})
        growth_potential = archetype_config.get('growth_potential', 0.5)
        
        # Salary range estimation
        salary_range = archetype_config.get('salary_range', (50000, 100000))
        
        # Generate learning path
        learning_path = self._generate_learning_path(skill_gaps, archetype)
        
        # Suggest alternative roles
        alternative_roles = self._suggest_alternative_roles(resume_analysis, archetype)
        
        # Market trends analysis
        market_trends = self._analyze_market_trends(archetype, resume_analysis)
        
        return MatchInsights(
            skill_gaps=skill_gaps,
            career_growth_potential=growth_potential,
            salary_range_match=salary_range,
            learning_path=learning_path,
            alternative_roles=alternative_roles,
            market_trends=market_trends
        )

    def _identify_skill_gaps(self, job: Any, archetype: str, resume_analysis: Dict[str, Any]) -> List[SkillMatch]:
        """Identify specific skill gaps with learning priorities"""
        archetype_config = self.job_archetypes.get(archetype, {})
        required_skills = archetype_config.get('required_skills', [])
        preferred_skills = archetype_config.get('preferred_skills', [])
        
        user_skills = set()
        skills_with_confidence = resume_analysis.get('skills_with_confidence', {})
        
        for category_skills in skills_with_confidence.values():
            for skill_data in category_skills:
                user_skills.add(skill_data['skill'].lower())
        
        skill_gaps = []
        
        # Check required skills
        for skill in required_skills:
            if skill.lower() not in user_skills:
                skill_gaps.append(SkillMatch(
                    skill=skill,
                    confidence=0.0,
                    skill_type='required',
                    frequency_in_jobs=self._get_skill_frequency(skill),
                    market_demand=self._get_market_demand(skill),
                    learning_priority=1
                ))
        
        # Check preferred skills
        for skill in preferred_skills:
            if skill.lower() not in user_skills:
                skill_gaps.append(SkillMatch(
                    skill=skill,
                    confidence=0.0,
                    skill_type='preferred',
                    frequency_in_jobs=self._get_skill_frequency(skill),
                    market_demand=self._get_market_demand(skill),
                    learning_priority=2
                ))
        
        return sorted(skill_gaps, key=lambda x: (x.learning_priority, -x.market_demand))

    def _get_skill_frequency(self, skill: str) -> int:
        """Get frequency of skill mentions across all jobs"""
        try:
            cache_key = f"skill_frequency_{skill.lower()}"
            frequency = cache.get(cache_key)
            
            if frequency is None:
                # For now, return a default value to avoid sync issues
                # In production, this should be precomputed or cached
                frequency = 10  # Default frequency
                cache.set(cache_key, frequency, 3600)  # Cache for 1 hour
            
            return frequency
        except Exception:
            return 0

    def _get_market_demand(self, skill: str) -> float:
        """Calculate market demand score for a skill"""
        # Find skill in taxonomy
        for category_data in self.skill_taxonomy.values():
            if skill in category_data['skills']:
                return category_data['demand_multiplier']
        
        return 1.0  # Default demand multiplier

    def _generate_learning_path(self, skill_gaps: List[SkillMatch], archetype: str) -> List[str]:
        """Generate personalized learning path based on skill gaps"""
        archetype_config = self.job_archetypes.get(archetype, {})
        career_path = archetype_config.get('career_path', [])
        
        # Priority order: required skills first, then by market demand
        required_skills = [gap.skill for gap in skill_gaps if gap.skill_type == 'required']
        preferred_skills = [gap.skill for gap in skill_gaps if gap.skill_type == 'preferred']
        
        learning_path = []
        
        # Add foundational skills first
        foundational_skills = {'Python', 'JavaScript', 'SQL', 'Git', 'HTML', 'CSS'}
        for skill in required_skills:
            if skill in foundational_skills:
                learning_path.append(f"Master {skill} fundamentals")
        
        # Add framework/advanced skills
        for skill in required_skills:
            if skill not in foundational_skills:
                learning_path.append(f"Learn {skill}")
        
        # Add preferred skills with lower priority
        for skill in preferred_skills[:3]:  # Limit to top 3
            learning_path.append(f"Consider learning {skill}")
        
        # Add soft skills based on career progression
        if 'senior' in archetype.lower() or 'lead' in archetype.lower():
            learning_path.append("Develop leadership and mentoring skills")
            learning_path.append("Improve system design and architecture knowledge")
        
        return learning_path[:6]  # Limit to 6 items

    def _suggest_alternative_roles(self, resume_analysis: Dict[str, Any], current_archetype: str) -> List[str]:
        """Suggest alternative roles based on current skills"""
        skills_with_confidence = resume_analysis.get('skills_with_confidence', {})
        user_skills = set()
        
        for category_skills in skills_with_confidence.values():
            for skill_data in category_skills:
                user_skills.add(skill_data['skill'].lower())
        
        alternative_scores = {}
        
        for archetype, config in self.job_archetypes.items():
            if archetype == current_archetype:
                continue
                
            score = 0
            total_skills = len(config['required_skills']) + len(config['preferred_skills'])
            
            # Calculate match score
            for skill in config['required_skills']:
                if skill.lower() in user_skills:
                    score += 2
            
            for skill in config['preferred_skills']:
                if skill.lower() in user_skills:
                    score += 1
            
            if total_skills > 0:
                alternative_scores[archetype] = score / total_skills
        
        # Return top 3 alternatives
        sorted_alternatives = sorted(alternative_scores.items(), key=lambda x: x[1], reverse=True)
        return [archetype.replace('_', ' ').title() for archetype, _ in sorted_alternatives[:3]]

    def _analyze_market_trends(self, archetype: str, resume_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Analyze market trends for skills and roles"""
        archetype_config = self.job_archetypes.get(archetype, {})
        
        # Simulate market trend analysis (in real implementation, this would use external APIs)
        trends = {
            'job_growth_rate': archetype_config.get('growth_potential', 0.5) * 100,
            'salary_trend': 15.0,  # Percentage increase year-over-year
            'skill_demand_trend': 20.0,  # Demand increase for key skills
            'remote_work_availability': 85.0,  # Percentage of remote positions
            'competition_level': 60.0  # Competition level (lower is better)
        }
        
        return trends

    def _calculate_confidence_level(self, scores: Dict[str, float], semantic_score: float, market_score: float) -> str:
        """Calculate confidence level of the match"""
        avg_score = (scores['skill_match'] + scores['experience_match'] + semantic_score + market_score) / 4
        
        if avg_score >= 80:
            return 'high'
        elif avg_score >= 60:
            return 'medium'
        else:
            return 'low'

    async def _update_resume_record(self, analysis: Dict[str, Any]):
        """Update resume record with enhanced analysis"""
        try:
            self.resume.analysis_summary = json.dumps(analysis)
            self.resume.extracted_skills = analysis.get('extracted_skills', [])
            self.resume.experience_level = analysis.get('experience_level', 'junior')
            await asyncio.to_thread(self.resume.save)
        except Exception as e:
            logger.error(f"Error updating resume record: {e}")

    async def generate_advanced_job_matches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Generate advanced job matches with ML-based scoring and insights
        """
        try:
            # Get enhanced resume analysis
            resume_analysis = await self.analyze_resume_advanced()
            
            if not resume_analysis:
                logger.warning("No resume analysis available for advanced job matching")
                return []
            
            # Get jobs with intelligent filtering
            jobs = await self._get_filtered_jobs(resume_analysis)
            
            # Process jobs in batches for better performance
            batch_size = 10
            job_matches = []
            
            for i in range(0, len(jobs), batch_size):
                batch = jobs[i:i + batch_size]
                batch_tasks = [
                    self.calculate_advanced_match_score(job, resume_analysis)
                    for job in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for job, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing job {job.id}: {result}")
                        continue
                    
                    if result['match_score'] > 20:  # Only include reasonable matches
                        job_matches.append({
                            'job': job,
                            'match_score': result['match_score'],
                            'score_breakdown': result['score_breakdown'],
                            'match_insights': result['match_insights'],
                            'archetype_match': result['archetype_match'],
                            'confidence_level': result['confidence_level']
                        })
            
            # Sort by match score and confidence
            job_matches.sort(key=lambda x: (x['match_score'], x['confidence_level'] == 'high'), reverse=True)
            
            # Save matches to database
            await self._save_advanced_job_matches(job_matches[:limit], resume_analysis)
            
            return job_matches[:limit]
            
        except Exception as e:
            logger.error(f"Error generating advanced job matches: {e}")
            return []

    async def _get_filtered_jobs(self, resume_analysis: Dict[str, Any]) -> List[Any]:
        """Get jobs filtered by user's skills and preferences"""
        try:
            # Extract user's key skills for filtering
            skills_with_confidence = resume_analysis.get('skills_with_confidence', {})
            key_skills = []
            
            for category_skills in skills_with_confidence.values():
                for skill_data in category_skills:
                    if skill_data['confidence'] > 0.5:  # High confidence skills
                        key_skills.append(skill_data['skill'])
            
            # Build query to find relevant jobs
            from django.db.models import Q
            from asgiref.sync import sync_to_async
            
            if key_skills:
                # Create Q objects for skill matching
                skill_queries = Q()
                for skill in key_skills[:10]:  # Limit to prevent query complexity
                    skill_queries |= (
                        Q(description__icontains=skill) |
                        Q(requirements__icontains=skill) |
                        Q(title__icontains=skill)
                    )
                
                jobs = await sync_to_async(list)(Job.objects.filter(
                    skill_queries,
                    is_active=True
                ).distinct().order_by('-created_at')[:300])  # Limit for performance
            else:
                # Fallback to recent jobs
                jobs = await sync_to_async(list)(Job.objects.filter(
                    is_active=True
                ).order_by('-created_at')[:200])
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error filtering jobs: {e}")
            return await sync_to_async(list)(Job.objects.filter(is_active=True).order_by('-created_at')[:100])

    async def _save_advanced_job_matches(self, matches: List[Dict[str, Any]], resume_analysis: Dict[str, Any]):
        """Save advanced job matches to database"""
        try:
            from asgiref.sync import sync_to_async
            
            # Create sync function for database operations
            def save_matches():
                with transaction.atomic():
                    # Clear existing matches
                    JobMatch.objects.filter(resume=self.resume).delete()
                    
                    # Create new matches
                    job_matches_to_create = []
                    for match in matches:
                        job_matches_to_create.append(JobMatch(
                            user=self.user,
                            resume=self.resume,
                            job=match['job'],
                            match_score=match['match_score'],
                            match_details=asdict(match['match_insights']) if hasattr(match['match_insights'], '__dict__') else match['match_insights'],
                            matching_skills=self._extract_matching_skills(match),
                            missing_skills=self._extract_missing_skills(match),
                            analysis_version='advanced_v2.0',
                            confidence_level=match['confidence_level'],
                            archetype_match=match['archetype_match']
                        ))
                    
                    # Bulk create for better performance
                    JobMatch.objects.bulk_create(job_matches_to_create)
            
            # Run the sync function asynchronously
            await sync_to_async(save_matches)()
            logger.info(f"Saved {len(matches)} advanced job matches for resume {self.resume.id}")
            
        except Exception as e:
            logger.error(f"Error saving advanced job matches: {e}")

    def _extract_matching_skills(self, match: Dict[str, Any]) -> List[str]:
        """Extract matching skills from match data"""
        # This would be implemented based on your JobMatch model structure
        return []

    def _extract_missing_skills(self, match: Dict[str, Any]) -> List[str]:
        """Extract missing skills from match insights"""
        insights = match.get('match_insights')
        if insights and hasattr(insights, 'skill_gaps'):
            return [gap.skill for gap in insights.skill_gaps[:5]]  # Top 5 gaps
        return []

    def generate_career_recommendations(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive career recommendations"""
        if not matches:
            return {
                'message': 'No suitable matches found. Focus on building fundamental skills.',
                'recommendations': ['Learn Python or JavaScript', 'Build portfolio projects', 'Gain practical experience']
            }
        
        # Analyze match patterns
        high_matches = [m for m in matches if m['match_score'] >= 75]
        medium_matches = [m for m in matches if 50 <= m['match_score'] < 75]
        
        # Aggregate insights
        all_skill_gaps = []
        archetype_counts = defaultdict(int)
        
        for match in matches[:20]:  # Top 20 matches
            insights = match.get('match_insights')
            if insights:
                all_skill_gaps.extend(insights.skill_gaps)
                archetype_counts[match['archetype_match']] += 1
        
        # Most common missing skills
        skill_gap_counter = Counter(gap.skill for gap in all_skill_gaps)
        top_skill_gaps = skill_gap_counter.most_common(6)
        
        # Most suitable career paths
        top_archetypes = Counter(archetype_counts).most_common(3)
        
        return {
            'match_summary': {
                'total_matches': len(matches),
                'high_quality_matches': len(high_matches),
                'medium_quality_matches': len(medium_matches),
                'average_match_score': sum(m['match_score'] for m in matches) / len(matches)
            },
            'top_skill_gaps': [skill for skill, count in top_skill_gaps],
            'recommended_career_paths': [archetype.replace('_', ' ').title() for archetype, _ in top_archetypes],
            'immediate_actions': self._generate_immediate_actions(high_matches, medium_matches, top_skill_gaps),
            'long_term_strategy': self._generate_long_term_strategy(top_archetypes, all_skill_gaps)
        }

    def _generate_immediate_actions(self, high_matches: List, medium_matches: List, skill_gaps: List) -> List[str]:
        """Generate immediate actionable recommendations"""
        actions = []
        
        if len(high_matches) >= 3:
            actions.append("Apply immediately to your top 3-5 matches")
            actions.append("Tailor your resume for each high-match position")
        elif len(medium_matches) >= 5:
            actions.append("Focus on improving skills for medium-match positions")
            actions.append("Apply to 2-3 medium matches as stretch opportunities")
        
        if skill_gaps:
            top_gap = skill_gaps[0][0]
            actions.append(f"Start learning {top_gap} immediately - it's in high demand")
        
        actions.append("Update your LinkedIn profile with your strongest skills")
        actions.append("Create a portfolio project showcasing your best work")
        
        return actions

    def _generate_long_term_strategy(self, top_archetypes: List, skill_gaps: List) -> List[str]:
        """Generate long-term career strategy"""
        strategy = []
        
        if top_archetypes:
            primary_archetype = top_archetypes[0][0]
            archetype_config = self.job_archetypes.get(primary_archetype, {})
            career_path = archetype_config.get('career_path', [])
            
            if career_path:
                strategy.append(f"Follow the {primary_archetype.replace('_', ' ').title()} career path")
                strategy.append(f"Next milestone: {career_path[-2] if len(career_path) > 1 else career_path[-1]}")
        
        # Skills development strategy
        required_skills = [gap.skill for gap in skill_gaps if gap.skill_type == 'required']
        if required_skills:
            strategy.append(f"Build expertise in: {', '.join(required_skills[:3])}")
        
        strategy.append("Gain 2-3 years experience in your chosen specialization")
        strategy.append("Develop leadership skills for senior roles")
        strategy.append("Stay updated with industry trends and emerging technologies")
        
        return strategy

    async def execute_complete_matching_workflow(self):
        """Execute the complete advanced job matching workflow"""
        try:
            logger.info(f"Starting complete advanced job matching workflow for resume {self.resume.id}")
            
            # Step 1: Advanced resume analysis
            resume_analysis = await self.analyze_resume_advanced()
            
            # Step 2: Generate advanced job matches
            matches = await self.generate_advanced_job_matches(limit=50)
            
            # Step 3: Generate career recommendations
            recommendations = self.generate_career_recommendations(matches)
            
            # Step 4: Update user's matching timestamp
            await self._update_matching_timestamp()
            
            # Step 5: Log results
            logger.info(f"Advanced job matching completed: {len(matches)} matches generated")
            
            return {
                'success': True,
                'matches_count': len(matches),
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in complete matching workflow: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _update_matching_timestamp(self):
        """Update the last matching timestamp"""
        try:
            if hasattr(self.resume, 'last_matched_at'):
                self.resume.last_matched_at = timezone.now()
                await asyncio.to_thread(self.resume.save, update_fields=['last_matched_at'])
        except Exception as e:
            logger.error(f"Error updating matching timestamp: {e}")

# Usage Example and Integration Functions

class JobMatchingService:
    """Service class for managing job matching operations"""
    
    @staticmethod
    async def match_user_with_jobs(user, resume):
        """Main entry point for job matching"""
        matcher = AdvancedJobMatcher(user, resume)
        return await matcher.execute_complete_matching_workflow()
    
    @staticmethod
    async def get_user_matches(user, resume, limit=20):
        """Get existing matches for a user"""
        try:
            from asgiref.sync import sync_to_async
            
            matches = await sync_to_async(list)(JobMatch.objects.filter(
                user=user,
                resume=resume,
                analysis_version='advanced_v2.0'
            ).order_by('-match_score')[:limit])
            
            return [{
                'job': match.job,
                'match_score': match.match_score,
                'confidence_level': match.confidence_level,
                'archetype_match': match.archetype_match,
                'match_details': match.match_details
            } for match in matches]
            
        except Exception as e:
            logger.error(f"Error getting user matches: {e}")
            return []
    
    @staticmethod
    async def refresh_matches_if_needed(user, resume):
        """Refresh matches if they're outdated"""
        try:
            # Check if matches need refresh (older than 24 hours)
            if hasattr(resume, 'last_matched_at') and resume.last_matched_at:
                time_diff = timezone.now() - resume.last_matched_at
                if time_diff < timedelta(hours=24):
                    return {'success': True, 'message': 'Matches are up to date'}
            
            # Refresh matches
            return await JobMatchingService.match_user_with_jobs(user, resume)
            
        except Exception as e:
            logger.error(f"Error refreshing matches: {e}")
            return {'success': False, 'error': str(e)}