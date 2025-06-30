"""
Enhanced Job Matcher with Intelligent Skill-Based Recommendations
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from django.apps import apps
from .enhanced_analyzer import EnhancedAIAnalyzer

logger = logging.getLogger(__name__)

# Dynamically load models
Job = apps.get_model('jobs', 'Job')
JobMatch = apps.get_model('jobs', 'JobMatch')

class EnhancedJobMatcher:
    """
    Enhanced job matcher that provides intelligent recommendations based on specific skills
    """
    
    def __init__(self, user, resume):
        self.user = user
        self.resume = resume
        self.analyzer = EnhancedAIAnalyzer()
        
        # Weight different skill categories for matching
        self.skill_weights = {
            'programming_languages': 1.0,
            'frameworks_libraries': 0.9,
            'databases': 0.8,
            'cloud_platforms': 0.8,
            'tools_technologies': 0.7,
            'experience_level': 0.6,
            'specialization': 0.9
        }
        
        # Technology stack patterns for job descriptions
        self.job_patterns = {
            'python_backend': {
                'required_skills': ['Python', 'Django', 'Flask', 'FastAPI'],
                'bonus_skills': ['PostgreSQL', 'Redis', 'Docker', 'AWS'],
                'keywords': ['python developer', 'backend developer', 'django developer', 'api development']
            },
            'react_frontend': {
                'required_skills': ['React', 'JavaScript', 'TypeScript'],
                'bonus_skills': ['Redux', 'Next.js', 'Tailwind CSS', 'GraphQL'],
                'keywords': ['frontend developer', 'react developer', 'javascript developer', 'ui developer']
            },
            'fullstack_web': {
                'required_skills': ['JavaScript', 'React', 'Node.js'],
                'bonus_skills': ['MongoDB', 'Express.js', 'AWS', 'Docker'],
                'keywords': ['full stack developer', 'fullstack developer', 'web developer', 'mern stack']
            },
            'data_science': {
                'required_skills': ['Python', 'Pandas', 'NumPy'],
                'bonus_skills': ['TensorFlow', 'PyTorch', 'Jupyter', 'SQL'],
                'keywords': ['data scientist', 'machine learning engineer', 'data analyst', 'ml engineer']
            },
            'devops': {
                'required_skills': ['Docker', 'Kubernetes', 'AWS'],
                'bonus_skills': ['Jenkins', 'Terraform', 'Ansible', 'Git'],
                'keywords': ['devops engineer', 'cloud engineer', 'platform engineer', 'sre']
            },
            'mobile_development': {
                'required_skills': ['React Native', 'Flutter', 'Swift', 'Kotlin'],
                'bonus_skills': ['Firebase', 'Redux', 'REST API'],
                'keywords': ['mobile developer', 'ios developer', 'android developer', 'app developer']
            }
        }

    def analyze_resume_for_matching(self) -> Dict[str, Any]:
        """
        Analyze resume specifically for job matching purposes
        """
        if hasattr(self.resume, 'analysis_summary') and self.resume.analysis_summary:
            try:
                # Try to parse existing analysis
                import json
                if isinstance(self.resume.analysis_summary, str):
                    existing_analysis = json.loads(self.resume.analysis_summary)
                else:
                    existing_analysis = self.resume.analysis_summary
                
                # Check if it's the enhanced format
                if 'extracted_skills' in existing_analysis and 'tech_stack_focus' in existing_analysis:
                    logger.info("Using existing enhanced analysis")
                    return existing_analysis
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Perform new enhanced analysis
        logger.info("Performing enhanced resume analysis for job matching")
        raw_text = getattr(self.resume, 'raw_text', '')
        
        if not raw_text:
            # Extract from file if raw_text is not available
            if hasattr(self.resume, 'file') and self.resume.file:
                try:
                    raw_text = self.analyzer.extract_text_from_pdf(self.resume.file.path)
                except Exception as e:
                    logger.error(f"Failed to extract text from resume file: {e}")
                    return {}
        
        if raw_text:
            analysis = self.analyzer.analyze_resume(raw_text)
            
            # Update resume with enhanced analysis
            self.resume.analysis_summary = json.dumps(analysis)
            self.resume.extracted_skills = analysis.get('extracted_skills', [])
            self.resume.experience_level = analysis.get('experience_level', 'junior')
            self.resume.save()
            
            return analysis
        
        return {}

    def calculate_job_match_score(self, job: Any, resume_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate detailed match score between job and resume with specific skill matching
        """
        job_title = job.title.lower()
        job_description = job.description.lower()
        job_requirements = getattr(job, 'requirements', '').lower()
        
        # Combine all job text for analysis
        job_text = f"{job_title} {job_description} {job_requirements}"
        
        # Extract user's skills from analysis
        user_skills = resume_analysis.get('extracted_skills', [])
        user_languages = resume_analysis.get('programming_languages', [])
        user_frameworks = resume_analysis.get('frameworks_libraries', [])
        user_databases = resume_analysis.get('databases', [])
        user_cloud = resume_analysis.get('cloud_platforms', [])
        user_tools = resume_analysis.get('tools_technologies', [])
        user_experience = resume_analysis.get('experience_level', 'junior')
        user_specialization = resume_analysis.get('specialization', '')
        
        # Initialize scoring
        total_score = 0.0
        max_possible_score = 0.0
        match_details = {
            'matched_skills': [],
            'missing_skills': [],
            'bonus_skills': [],
            'experience_match': False,
            'specialization_match': False
        }
        
        # 1. Core skill matching (40% of total score)
        core_skill_score = 0.0
        core_max_score = 40.0
        
        all_user_skills = user_skills + user_languages + user_frameworks + user_databases + user_cloud + user_tools
        all_user_skills_lower = [skill.lower() for skill in all_user_skills]
        
        # Check for exact skill matches in job description with intelligent weighting
        skill_matches_count = 0
        high_value_matches = 0
        
        for skill in all_user_skills:
            skill_lower = skill.lower()
            
            # Multiple patterns to catch skill mentions
            patterns = [
                rf'\b{re.escape(skill_lower)}\b',  # Exact match
                rf'{re.escape(skill_lower)}\s*(?:\d+|\+|\.x)',  # With versions
                rf'(?:experience\s+with|proficient\s+in|knowledge\s+of)\s+{re.escape(skill_lower)}\b',  # Context patterns
            ]
            
            skill_found = False
            for pattern in patterns:
                if re.search(pattern, job_text):
                    skill_found = True
                    break
            
            if skill_found:
                skill_matches_count += 1
                match_details['matched_skills'].append(skill)
                
                # Categorize and weight different skill types
                if skill in user_languages:
                    core_skill_score += 5.0  # Programming languages are critical
                    high_value_matches += 1
                elif skill in user_frameworks:
                    core_skill_score += 4.5  # Frameworks are very important
                    high_value_matches += 1
                elif skill in user_databases:
                    core_skill_score += 4.0  # Database skills are important
                elif skill in user_cloud:
                    core_skill_score += 4.0  # Cloud skills are important
                elif skill in user_tools:
                    core_skill_score += 2.5  # Tools are moderately important
                else:
                    core_skill_score += 2.0  # Other technologies
        
        # Bonus for having multiple high-value skill matches
        if high_value_matches >= 3:
            core_skill_score += 5.0  # Excellent skill alignment
        elif high_value_matches >= 2:
            core_skill_score += 3.0  # Good skill alignment
        
        # Cap core skill score at maximum
        core_skill_score = min(core_skill_score, core_max_score)
        total_score += core_skill_score
        max_possible_score += core_max_score
        
        # 2. Technology stack matching (25% of total score)
        stack_score = 0.0
        stack_max_score = 25.0
        
        # Identify which tech stack this job belongs to
        job_stack = self._identify_job_tech_stack(job_text)
        user_stack = resume_analysis.get('tech_stack_focus', '').lower()
        
        if job_stack and user_stack:
            # Check if stacks align
            if job_stack in user_stack or user_stack in job_stack:
                stack_score += 15.0
                match_details['specialization_match'] = True
            
            # Check for stack-specific skills
            if job_stack in self.job_patterns:
                pattern = self.job_patterns[job_stack]
                
                # Required skills for this stack
                required_matches = 0
                for req_skill in pattern['required_skills']:
                    if req_skill.lower() in all_user_skills_lower:
                        required_matches += 1
                
                # Bonus for having most required skills
                if required_matches >= len(pattern['required_skills']) * 0.7:
                    stack_score += 10.0
                
                # Bonus skills
                bonus_matches = 0
                for bonus_skill in pattern['bonus_skills']:
                    if bonus_skill.lower() in all_user_skills_lower:
                        bonus_matches += 1
                        match_details['bonus_skills'].append(bonus_skill)
                
                stack_score += min(bonus_matches * 2.0, 10.0)
        
        total_score += stack_score
        max_possible_score += stack_max_score
        
        # 3. Experience level matching (20% of total score)
        exp_score = 0.0
        exp_max_score = 20.0
        
        # Extract experience requirements from job
        job_exp_level = self._extract_job_experience_level(job_text)
        user_exp_level = user_experience.lower()
        
        # Experience level compatibility
        exp_levels = {'entry': 0, 'junior': 1, 'middle': 2, 'senior': 3, 'lead': 4}
        user_level_num = exp_levels.get(user_exp_level, 1)
        job_level_num = exp_levels.get(job_exp_level, 1)
        
        if user_level_num >= job_level_num:
            exp_score = exp_max_score  # Perfect match or overqualified
            match_details['experience_match'] = True
        elif user_level_num == job_level_num - 1:
            exp_score = exp_max_score * 0.8  # Close match
        elif user_level_num == job_level_num - 2:
            exp_score = exp_max_score * 0.5  # Stretch opportunity
        else:
            exp_score = exp_max_score * 0.2  # Significant gap
        
        total_score += exp_score
        max_possible_score += exp_max_score
        
        # 4. Specialization/Domain matching (15% of total score)
        domain_score = 0.0
        domain_max_score = 15.0
        
        if user_specialization:
            # Check if specialization keywords appear in job
            spec_keywords = user_specialization.lower().split()
            for keyword in spec_keywords:
                if keyword in job_text and len(keyword) > 3:  # Avoid matching short words
                    domain_score += 3.0
        
        domain_score = min(domain_score, domain_max_score)
        total_score += domain_score
        max_possible_score += domain_max_score
        
        # Calculate final percentage
        final_score = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        final_score = min(max(final_score, 0), 100)  # Ensure 0-100 range
        
        # Identify missing critical skills
        missing_skills = self._identify_missing_skills(job_text, all_user_skills_lower)
        match_details['missing_skills'] = missing_skills
        
        return {
            'match_score': round(final_score, 1),
            'match_details': match_details,  # Use consistent key name
            'breakdown': {
                'core_skills': round((core_skill_score / core_max_score) * 100, 1),
                'tech_stack': round((stack_score / stack_max_score) * 100, 1),
                'experience': round((exp_score / exp_max_score) * 100, 1),
                'specialization': round((domain_score / domain_max_score) * 100, 1)
            }
        }

    def _identify_job_tech_stack(self, job_text: str) -> str:
        """
        Intelligently identify the primary technology stack for a job based on its description
        """
        job_text_lower = job_text.lower()
        stack_scores = {}
        
        for stack_name, pattern in self.job_patterns.items():
            score = 0
            
            # Check for stack-specific keywords with word boundaries
            for keyword in pattern['keywords']:
                if re.search(rf'\b{re.escape(keyword.lower())}\b', job_text_lower):
                    score += 3
            
            # Check for required skills (higher weight)
            for skill in pattern['required_skills']:
                if re.search(rf'\b{re.escape(skill.lower())}\b', job_text_lower):
                    score += 5
            
            # Check for bonus skills
            for skill in pattern['bonus_skills']:
                if re.search(rf'\b{re.escape(skill.lower())}\b', job_text_lower):
                    score += 2
            
            # Additional context-based scoring
            if stack_name == 'python_backend':
                if re.search(r'backend.*python|python.*backend|api.*python|python.*api', job_text_lower):
                    score += 5
            elif stack_name == 'react_frontend':
                if re.search(r'frontend.*react|react.*frontend|ui.*react|react.*ui', job_text_lower):
                    score += 5
            elif stack_name == 'fullstack_web':
                if re.search(r'full.?stack|frontend.*backend|web.*developer', job_text_lower):
                    score += 5
            elif stack_name == 'data_science':
                if re.search(r'data.*scientist|machine.*learning|ml.*engineer', job_text_lower):
                    score += 5
            elif stack_name == 'devops':
                if re.search(r'devops|cloud.*engineer|platform.*engineer|sre', job_text_lower):
                    score += 5
            elif stack_name == 'mobile_development':
                if re.search(r'mobile.*developer|ios.*developer|android.*developer', job_text_lower):
                    score += 5
            
            if score > 0:
                stack_scores[stack_name] = score
        
        # Return the stack with highest score (minimum threshold)
        if stack_scores:
            best_stack = max(stack_scores, key=stack_scores.get)
            if stack_scores[best_stack] >= 4:  # Minimum confidence threshold
                return best_stack
        
        return 'general_development'

    def _extract_job_experience_level(self, job_text: str) -> str:
        """
        Extract experience level requirement from job description
        """
        if re.search(r'senior|lead|principal|staff|architect', job_text):
            return 'senior'
        elif re.search(r'mid-level|intermediate|3\+.*years?|4\+.*years?|5\+.*years?', job_text):
            return 'middle'
        elif re.search(r'junior|entry|1-2.*years?|0-2.*years?|recent.*graduate', job_text):
            return 'junior'
        elif re.search(r'intern|trainee|graduate|entry.*level', job_text):
            return 'entry'
        else:
            return 'junior'  # Default

    def _identify_missing_skills(self, job_text: str, user_skills: List[str]) -> List[str]:
        """
        Intelligently identify specific skills mentioned in job that user doesn't have
        """
        job_text_lower = job_text.lower()
        user_skills_lower = [skill.lower() for skill in user_skills]
        missing_skills = []
        
        # Comprehensive skill database for job requirements
        all_possible_skills = []
        for category_skills in self.analyzer.skill_categories.values():
            all_possible_skills.extend(category_skills)
        
        # Look for specific skills mentioned in the job
        for skill in all_possible_skills:
            skill_lower = skill.lower()
            
            # Skip if user already has this skill
            if skill_lower in user_skills_lower:
                continue
            
            # Check if skill is mentioned in job description with context
            skill_patterns = [
                rf'\b{re.escape(skill_lower)}\b',
                rf'(?:experience\s+with|knowledge\s+of|proficient\s+in|familiar\s+with)\s+{re.escape(skill_lower)}\b',
                rf'{re.escape(skill_lower)}\s+(?:experience|skills|knowledge)',
                rf'(?:required|must\s+have|should\s+have|need).*{re.escape(skill_lower)}\b',
            ]
            
            for pattern in skill_patterns:
                if re.search(pattern, job_text_lower):
                    missing_skills.append(skill)
                    break  # Avoid duplicates
        
        # Also look for technology patterns that might not be in our database
        tech_patterns = [
            r'(?:experience\s+with|knowledge\s+of|proficient\s+in)\s+([A-Za-z][A-Za-z0-9\.\-]{2,15})\b',
            r'(\w+(?:\.\w+)*)\s+(?:framework|library|database|platform|language)',
            r'(?:required|must\s+have).*?(\w+(?:\.\w+)*)\s+(?:skills|experience)',
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, job_text_lower, re.IGNORECASE)
            for match in matches:
                skill_candidate = match.strip()
                # Filter out common words and add only if it looks like a technology
                if (len(skill_candidate) > 2 and 
                    skill_candidate not in ['and', 'the', 'for', 'with', 'are', 'have', 'will', 'can', 'work', 'team'] and
                    skill_candidate.lower() not in user_skills_lower and
                    skill_candidate not in missing_skills):
                    missing_skills.append(skill_candidate.title())
        
        # Limit to most important missing skills and remove duplicates
        unique_missing = []
        for skill in missing_skills:
            if skill not in unique_missing:
                unique_missing.append(skill)
        
        return unique_missing[:8]  # Return top 8 missing skills

    def generate_job_matches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Generate enhanced job matches with detailed scoring
        """
        # Get resume analysis
        resume_analysis = self.analyze_resume_for_matching()
        
        if not resume_analysis:
            logger.warning("No resume analysis available for job matching")
            return []
        
        # Get all jobs (you might want to add filtering here)
        jobs = Job.objects.all().order_by('-created_at')[:200]  # Limit for performance
        
        job_matches = []
        
        for job in jobs:
            try:
                match_result = self.calculate_job_match_score(job, resume_analysis)
                
                job_matches.append({
                    'job': job,
                    'match_score': match_result['match_score'],
                    'match_details': match_result['match_details'],  # Fixed: use correct key
                    'score_breakdown': match_result['breakdown']
                })
                
            except Exception as e:
                logger.error(f"Error calculating match for job {job.id}: {e}")
                continue
        
        # Sort by match score
        job_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Save top matches to database
        self._save_job_matches(job_matches[:limit], resume_analysis)
        
        return job_matches[:limit]

    def _save_job_matches(self, matches: List[Dict[str, Any]], resume_analysis: Dict[str, Any]):
        """
        Save job matches to database for faster future retrieval
        """
        try:
            # Clear existing matches for this resume
            JobMatch.objects.filter(resume=self.resume).delete()
            
            # Create new matches
            for match in matches:
                JobMatch.objects.create(
                    resume=self.resume,
                    job=match['job'],
                    match_score=match['match_score'],
                    match_details=match['match_details'],
                    analysis_version='enhanced_v1'
                )
            
            logger.info(f"Saved {len(matches)} job matches for resume {self.resume.id}")
            
        except Exception as e:
            logger.error(f"Error saving job matches: {e}")

    def get_recommendations_summary(self, matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of recommendations and insights
        """
        if not matches:
            return {'message': 'No suitable job matches found. Consider expanding your skill set.'}
        
        high_matches = [m for m in matches if m['match_score'] >= 75]
        medium_matches = [m for m in matches if 50 <= m['match_score'] < 75]
        low_matches = [m for m in matches if m['match_score'] < 50]
        
        # Analyze most common missing skills
        all_missing = []
        for match in matches[:20]:  # Top 20 jobs
            all_missing.extend(match['match_details'].get('missing_skills', []))
        
        from collections import Counter
        skill_gaps = Counter(all_missing).most_common(5)
        
        return {
            'total_matches': len(matches),
            'high_quality_matches': len(high_matches),
            'medium_quality_matches': len(medium_matches),
            'low_quality_matches': len(low_matches),
            'top_skill_gaps': [skill for skill, count in skill_gaps],
            'recommendation': self._generate_recommendation(high_matches, medium_matches, skill_gaps)
        }

    def _generate_recommendation(self, high_matches: List, medium_matches: List, skill_gaps: List) -> str:
        """
        Generate personalized recommendations
        """
        if len(high_matches) >= 5:
            return "Excellent! You have strong matches for multiple positions. Focus on applying to your top matches."
        elif len(high_matches) >= 2:
            return "Good matches found! Apply to high-scoring positions and consider improving skills for medium matches."
        elif len(medium_matches) >= 5:
            return "Several potential opportunities. Consider learning these in-demand skills to improve your match scores."
        elif skill_gaps:
            top_gaps = [gap[0] for gap in skill_gaps[:3]]
            return f"Consider learning these in-demand skills: {', '.join(top_gaps)}. This will significantly improve your job prospects."
        else:
            return "Keep building your skills and gaining experience. The job market has opportunities for continuous learners."

    def find_and_create_job_matches(self):
        """
        Complete workflow: analyze resume, find matches, and save them
        """
        try:
            logger.info(f"Starting enhanced job matching for resume {self.resume.id}")
            
            # Generate job matches using enhanced algorithm
            matches = self.generate_job_matches(limit=50)
            
            if matches:
                # Save the matches to database
                resume_analysis = self.analyze_resume_for_matching()
                self._save_job_matches(matches, resume_analysis)
                
                # Log summary
                summary = self.get_recommendations_summary(matches)
                logger.info(f"Enhanced job matching completed: {summary['total_matches']} total matches, "
                           f"{summary['high_quality_matches']} high-quality matches")
            else:
                logger.warning(f"No job matches found for resume {self.resume.id}")
                
        except Exception as e:
            logger.error(f"Error in enhanced job matching workflow: {e}")
            raise
