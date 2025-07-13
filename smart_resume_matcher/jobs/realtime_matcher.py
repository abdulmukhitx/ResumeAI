"""
Real-time job matcher that works with fresh HH API data
"""
import logging
from typing import List, Dict, Any, Optional
from .enhanced_hh_client import EnhancedHHApiClient, JobData
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JobMatch:
    """Data class for job match results"""
    job: JobData
    match_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    match_explanation: str
    confidence_level: str

class RealTimeJobMatcher:
    """Real-time job matcher using fresh HH API data"""
    
    def __init__(self, user_skills: List[str], user_experience: str = '', user_location: str = ''):
        self.user_skills = [skill.lower() for skill in user_skills] if user_skills else []
        self.user_experience = user_experience.lower()
        self.user_location = user_location
        self.hh_client = EnhancedHHApiClient()
        
    def calculate_match_score(self, job: JobData) -> Dict[str, Any]:
        """Calculate match score between user profile and job"""
        
        # Extract job skills (normalize to lowercase)
        job_skills = [skill.lower() for skill in job.skills]
        
        # 1. Skills matching (40% weight)
        if self.user_skills and job_skills:
            matched_skills = list(set(self.user_skills).intersection(set(job_skills)))
            skills_match_ratio = len(matched_skills) / len(job_skills)
            skills_score = min(skills_match_ratio * 1.5, 1.0)  # Boost good matches
        else:
            matched_skills = []
            skills_score = 0.0
        
        # 2. Experience matching (30% weight)
        experience_score = self._calculate_experience_match(job.experience_required)
        
        # 3. Title/keyword matching (20% weight)
        title_score = self._calculate_title_match(job.title, job.description)
        
        # 4. Tech job bonus (10% weight)
        tech_bonus = self._calculate_tech_bonus(job.title, job.description)
        
        # Calculate overall score
        overall_score = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            title_score * 0.2 +
            tech_bonus * 0.1
        )
        
        # Boost score for jobs with many matched skills
        if len(matched_skills) >= 3:
            overall_score = min(overall_score + 0.15, 1.0)
        elif len(matched_skills) >= 2:
            overall_score = min(overall_score + 0.10, 1.0)
        
        # Calculate missing skills
        missing_skills = list(set(job_skills) - set(self.user_skills))
        
        # Generate confidence level
        confidence_level = self._get_confidence_level(overall_score, len(matched_skills))
        
        # Generate explanation
        explanation = self._generate_match_explanation(
            skills_score, experience_score, title_score, matched_skills
        )
        
        return {
            'match_score': min(overall_score * 100, 100),  # Convert to percentage
            'matching_skills': [skill.title() for skill in matched_skills],
            'missing_skills': [skill.title() for skill in missing_skills],
            'match_explanation': explanation,
            'confidence_level': confidence_level
        }
    
    def _calculate_experience_match(self, job_experience: str) -> float:
        """Calculate experience level match"""
        if not job_experience:
            return 0.5  # Neutral if no experience specified
        
        job_exp_lower = job_experience.lower()
        
        # Experience level mapping
        user_exp_level = 2  # Default middle level
        if 'junior' in self.user_experience or 'entry' in self.user_experience:
            user_exp_level = 1
        elif 'middle' in self.user_experience or 'mid' in self.user_experience:
            user_exp_level = 2
        elif 'senior' in self.user_experience or 'lead' in self.user_experience:
            user_exp_level = 3
        
        # Job experience requirements
        job_exp_level = 2  # Default
        if any(term in job_exp_lower for term in ['junior', 'entry', 'начинающий', '1-2', '0-1']):
            job_exp_level = 1
        elif any(term in job_exp_lower for term in ['middle', 'mid', 'средний', '2-5', '3-5']):
            job_exp_level = 2
        elif any(term in job_exp_lower for term in ['senior', 'lead', 'старший', '5+', '6+']):
            job_exp_level = 3
        
        # Calculate score based on level difference
        diff = abs(user_exp_level - job_exp_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.4
    
    def _calculate_title_match(self, job_title: str, job_description: str) -> float:
        """Calculate title/keyword match"""
        if not self.user_skills:
            return 0.5
        
        # Combine title and description
        combined_text = f"{job_title} {job_description}".lower()
        
        # Check for user skills in job text
        matches = 0
        for skill in self.user_skills:
            if skill in combined_text:
                matches += 1
        
        if self.user_skills:
            return min(matches / len(self.user_skills), 1.0)
        return 0.5
    
    def _calculate_tech_bonus(self, job_title: str, job_description: str) -> float:
        """Calculate tech job bonus"""
        tech_keywords = [
            'developer', 'engineer', 'programmer', 'разработчик', 'программист',
            'архитектор', 'analyst', 'scientist', 'devops', 'qa', 'тестировщик'
        ]
        
        combined_text = f"{job_title} {job_description}".lower()
        
        # Check if it's a tech job
        for keyword in tech_keywords:
            if keyword in combined_text:
                return 1.0
        
        return 0.0
    
    def _get_confidence_level(self, score: float, matched_skills_count: int) -> str:
        """Get confidence level based on score and matched skills"""
        if score >= 0.8 and matched_skills_count >= 3:
            return 'high'
        elif score >= 0.6 and matched_skills_count >= 2:
            return 'medium'
        elif score >= 0.4 and matched_skills_count >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def _generate_match_explanation(self, skills_score: float, exp_score: float, 
                                  title_score: float, matched_skills: List[str]) -> str:
        """Generate human-readable match explanation"""
        explanations = []
        
        if skills_score >= 0.7:
            explanations.append(f"Strong skills alignment with {len(matched_skills)} matching skills")
        elif skills_score >= 0.4:
            explanations.append(f"Good skills match with {len(matched_skills)} relevant skills")
        elif matched_skills:
            explanations.append(f"Some skills overlap ({len(matched_skills)} matching)")
        else:
            explanations.append("Limited skills overlap")
        
        if exp_score >= 0.8:
            explanations.append("experience level matches well")
        elif exp_score >= 0.6:
            explanations.append("experience level is suitable")
        
        if title_score >= 0.6:
            explanations.append("job requirements align with your profile")
        
        return ". ".join(explanations).capitalize() + "."
    
    def find_matching_jobs(self, search_query: str = '', location: str = '', 
                         max_jobs: int = 50) -> List[JobMatch]:
        """Find matching jobs using real-time HH API data"""
        logger.info(f"Starting real-time job matching: query='{search_query}', location='{location}'")
        
        # Generate search query from skills if not provided
        if not search_query and self.user_skills:
            search_query = self.hh_client.generate_search_query_from_skills(self.user_skills)
            logger.info(f"Generated search query from skills: '{search_query}'")
        
        # Use user location if not provided
        if not location:
            location = self.user_location
        
        # Fetch fresh jobs from HH APIs
        jobs = self.hh_client.search_jobs_realtime(
            search_query=search_query,
            location=location,
            max_total=max_jobs * 2  # Fetch more to filter better matches
        )
        
        if not jobs:
            logger.warning("No jobs found from HH APIs")
            return []
        
        # Calculate match scores for all jobs
        job_matches = []
        for job in jobs:
            match_data = self.calculate_match_score(job)
            
            # Only include jobs with reasonable match scores
            if match_data['match_score'] >= 5:  # Minimum 5% match
                job_match = JobMatch(
                    job=job,
                    match_score=match_data['match_score'],
                    matching_skills=match_data['matching_skills'],
                    missing_skills=match_data['missing_skills'],
                    match_explanation=match_data['match_explanation'],
                    confidence_level=match_data['confidence_level']
                )
                job_matches.append(job_match)
        
        # Sort by match score (highest first)
        job_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # Limit results
        final_matches = job_matches[:max_jobs]
        
        logger.info(f"Real-time job matching completed: {len(final_matches)} matches found")
        return final_matches
