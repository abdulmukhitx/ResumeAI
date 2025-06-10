import requests
import logging
from django.conf import settings
from django.apps import apps
from typing import List, Dict, Any, Optional, Union
from resumes.utils import AIAnalyzer

logger = logging.getLogger(__name__)

class HHApiClient:
    # City/country name to HH.ru area ID mapping
    LOCATION_MAPPING = {
        'almaty': '160',
        'nur-sultan': '159',  # Now Astana
        'astana': '159',
        'shymkent': '202',
        'karaganda': '161',
        'aktau': '182',
        'atyrau': '181',
        'kazakhstan': '40',  # Country code
        'moscow': '1',
        'saint petersburg': '2',
        'st petersburg': '2',
        'russia': '113',  # Country code
        'novosibirsk': '4',
        'yekaterinburg': '3',
    }
    
    def __init__(self):
        self.base_url = settings.HH_API_BASE_URL
        self.user_agent = settings.HH_API_USER_AGENT
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
        }
    
    def _resolve_location(self, location: Optional[Union[str, int]]) -> Optional[str]:
        """
        Resolve location string or ID to valid HH.ru area ID
        Handles comma-separated locations like "City, Country"
        """
        if location is None:
            return '1'  # Default to Moscow
            
        # If already a digit, assume it's a valid ID
        if isinstance(location, int) or (isinstance(location, str) and str(location).isdigit()):
            return str(location)
            
        # Handle string locations
        if isinstance(location, str):
            location = location.lower().strip()
            
            # Handle comma-separated values like "Almaty, Kazakhstan"
            if ',' in location:
                location_parts = [part.strip() for part in location.split(',')]
                
                # Try the city first (first part)
                city = location_parts[0]
                if city in self.LOCATION_MAPPING:
                    return self.LOCATION_MAPPING[city]
                
                # Try the country (last part)
                country = location_parts[-1]
                if country in self.LOCATION_MAPPING:
                    return self.LOCATION_MAPPING[country]
            
            # Direct lookup
            if location in self.LOCATION_MAPPING:
                return self.LOCATION_MAPPING[location]
        
        logger.info(f"Could not resolve location '{location}', defaulting to Moscow")
        return '1'  # Default to Moscow if not found
    
    def search_vacancies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search vacancies on HH.ru"""
        url = f"{self.base_url}/vacancies"
        
        # Clean parameters - remove empty/None values
        clean_params = {k: v for k, v in params.items() if v}
        
        # Handle area parameter using our location resolver
        if 'area' in clean_params:
            area_value = clean_params['area']
            resolved_area = self._resolve_location(area_value)
            clean_params['area'] = resolved_area
            logger.info(f"Resolved location '{area_value}' to area ID '{resolved_area}'")
        else:
            # Set default area to Moscow (1) if not provided
            clean_params['area'] = '1'
        
        try:
            logger.info(f"Searching HH.ru with parameters: {clean_params}")
            response = requests.get(url, headers=self.headers, params=clean_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"HH.ru API request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific vacancy"""
        url = f"{self.base_url}/vacancies/{vacancy_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"HH.ru API request failed: {str(e)}") from e
            
    def get_areas(self) -> List[Dict[str, Any]]:
        """
        Get the complete areas dictionary from HH.ru API
        This can be used to build a more comprehensive location mapping
        """
        url = f"{self.base_url}/areas"
        
        try:
            logger.info(f"Fetching areas dictionary from HH.ru API")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"HH.ru API request failed while fetching areas: {str(e)}"
            logger.error(error_msg)
            return []

class JobMatcher:
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
    
    def calculate_match_score(self, resume_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Calculate matching score between resume and job"""
        
        # Extract data
        resume_skills = set([skill.lower() for skill in resume_data.get('extracted_skills', [])])
        job_skills = set([skill.lower() for skill in job_data.get('required_skills', [])])
        
        # Skills matching
        matched_skills = resume_skills.intersection(job_skills)
        skills_score = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # Experience level matching
        resume_exp = resume_data.get('experience_level', '').lower()
        job_exp_req = job_data.get('experience_required', '').lower()
        experience_score = self._match_experience_level(resume_exp, job_exp_req)
        
        # Title matching
        resume_titles = [title.lower() for title in resume_data.get('job_titles', [])]
        job_title = job_data.get('title', '').lower()
        title_score = self._match_titles(resume_titles, job_title)
        
        # Overall score calculation
        overall_score = (
            skills_score * 0.4 +
            experience_score * 0.3 +
            title_score * 0.3
        )
        
        return {
            'overall_score': min(overall_score, 1.0),
            'skills_score': skills_score,
            'experience_score': experience_score,
            'title_score': title_score,
            'matched_skills': list(matched_skills),
            'missing_skills': list(job_skills - resume_skills),
            'match_explanation': self._generate_explanation(
                skills_score, experience_score, title_score, matched_skills
            )
        }
    
    def _match_experience_level(self, resume_exp: str, job_exp: str) -> float:
        """Match experience levels"""
        exp_levels = {
            'entry': 1, 'junior': 2, 'middle': 3, 'senior': 4, 'lead': 5
        }
        
        resume_level = exp_levels.get(resume_exp, 2)
        
        # Extract job experience requirements
        if 'junior' in job_exp or '1-3' in job_exp:
            job_level = 2
        elif 'middle' in job_exp or '3-5' in job_exp:
            job_level = 3
        elif 'senior' in job_exp or '5+' in job_exp:
            job_level = 4
        else:
            job_level = 2  # default
        
        # Calculate score based on level difference
        diff = abs(resume_level - job_level)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.8
        elif diff == 2:
            return 0.5
        else:
            return 0.2
    
    def _match_titles(self, resume_titles: List[str], job_title: str) -> float:
        """Match job titles"""
        if not resume_titles or not job_title:
            return 0.5
        
        # Simple keyword matching
        job_words = set(job_title.split())
        best_score = 0
        
        for title in resume_titles:
            title_words = set(title.split())
            common_words = job_words.intersection(title_words)
            score = len(common_words) / len(job_words) if job_words else 0
            best_score = max(best_score, score)
        
        return best_score
    
    def _generate_explanation(self, skills_score: float, exp_score: float, 
                           title_score: float, matched_skills: List[str]) -> str:
        """Generate human-readable match explanation"""
        explanation = []
        
        if skills_score > 0.7:
            explanation.append(f"Strong skills match ({len(matched_skills)} matching skills)")
        elif skills_score > 0.4:
            explanation.append(f"Good skills match ({len(matched_skills)} matching skills)")
        else:
            explanation.append("Limited skills overlap")
        
        if exp_score > 0.8:
            explanation.append("Experience level aligns well")
        elif exp_score > 0.5:
            explanation.append("Experience level is close")
        else:
            explanation.append("Experience level differs significantly")
        
        if title_score > 0.6:
            explanation.append("Job title matches previous roles")
        
        return ". ".join(explanation) + "."