"""
AI-powered job matching functionality to find the best job opportunities
based on skills, experience, and education from uploaded resumes.
Updated to support all professions, not just technology.
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional, Set
from django.utils import timezone
from django.apps import apps
from .services import HHApiClient
from resumes.universal_skills import (
    UNIVERSAL_SKILLS_DATABASE, 
    identify_profession_category,
    get_profession_search_terms,
    get_all_skills_for_profession
)

# Get models dynamically to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
Job = apps.get_model('jobs', 'Job')
JobMatch = apps.get_model('jobs', 'JobMatch')
JobSearch = apps.get_model('jobs', 'JobSearch')

logger = logging.getLogger(__name__)

class JobMatcher:
    """
    AI-powered job matching functionality that:
    - Uses analyzed resume data to find best job opportunities across all professions
    - Retrieves relevant jobs from HH.ru API
    - Ranks and presents jobs based on match score
    - Supports healthcare, legal, education, finance, and all other professions
    """
    
    def __init__(self, user=None, resume=None):
        """
        Initialize the JobMatcher with user and resume
        
        Args:
            user: Django User object
            resume: Resume object from database
        """
        self.user = user
        self.resume = resume
        self.api_client = HHApiClient()
        
    def fetch_relevant_jobs(self, search_query: str, location: Optional[str] = None, 
                           page: int = 0, per_page: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch relevant job listings from HH.ru API based on search query
        
        Args:
            search_query: Job search query (can be auto-generated from resume)
            location: Location string to search in
            page: Page number for pagination
            per_page: Number of results per page
        
        Returns:
            List of fetched job dictionaries
        """
        # Prepare search parameters
        search_params = {
            'text': search_query,
            'page': page,
            'per_page': per_page
        }
        
        # Add location if provided
        if location:
            search_params['area'] = location
            
        # Call API
        try:
            search_results = self.api_client.search_vacancies(search_params)
            return search_results.get('items', [])
        except Exception as e:
            logger.error("Error fetching jobs: %s", str(e))
            return []
    
    def generate_search_query_from_resume(self) -> str:
        """
        Generate an optimal search query based on resume data using universal skills
        """
        if not self.resume:
            return "professional"
            
        # Identify the profession category from resume
        job_titles = getattr(self.resume, 'job_titles', [])
        skills = getattr(self.resume, 'extracted_skills', [])
        resume_text = getattr(self.resume, 'content', '') or getattr(self.resume, 'text', '') or ''
        
        # Identify profession category
        profession_category = identify_profession_category(
            resume_text=resume_text,
            job_titles=job_titles
        )
        
        # Get profession-specific search terms
        search_terms = get_profession_search_terms(
            profession_category=profession_category,
            job_titles=job_titles,
            skills=skills
        )
        
        # Use the most relevant search term
        if search_terms:
            return search_terms[0]
        
        return "professional"
    
    def _extract_skills_from_job(self, job_data: Dict[str, Any]) -> Set[str]:
        """
        Extract skills from job description and requirements using universal skills database
        
        Args:
            job_data: Job dictionary containing description and requirements
        
        Returns:
            Set of extracted skills across all professions
        """
        if not job_data:
            return set()
            
        # Safely get nested dict values
        snippet_req = job_data.get('snippet', {}).get('requirement', '') if job_data.get('snippet') else ''
        snippet_resp = job_data.get('snippet', {}).get('responsibility', '') if job_data.get('snippet') else ''
        
        # Combine description and requirements, ensuring all values are strings
        text_parts = [
            job_data.get('description') or '',
            job_data.get('requirements') or '',
            snippet_req or '',
            snippet_resp or ''
        ]
        # Filter out None values and empty strings, then join
        full_text = ' '.join([str(part) for part in text_parts if part]).lower()
        
        # Extract skills from all profession categories
        skills = set()
        
        # Check each profession category and extract matching skills
        for subcategories in UNIVERSAL_SKILLS_DATABASE.values():
            for skill_list in subcategories.values():
                for skill in skill_list:
                    # Create regex pattern for skill matching
                    skill_lower = skill.lower()
                    # Replace special characters and create word boundary pattern
                    pattern = r'\b' + re.escape(skill_lower).replace(r'\ ', r'[ -]?') + r'\b'
                    if re.search(pattern, full_text):
                        skills.add(skill_lower)
                
        return skills

    def calculate_match_score(self, job_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate match score between resume and job for any profession
        
        Args:
            job_data: Job dictionary with title, description, requirements, etc.
        
        Returns:
            Tuple of (match_score, match_details)
        """
        if not self.resume:
            return 0.0, {}
        
        # Extract job skills using universal skills
        job_skills = self._extract_skills_from_job(job_data)
        
        # Get resume skills
        resume_skills = set([skill.lower() for skill in getattr(self.resume, 'extracted_skills', [])])
        
        # Calculate skill match
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        
        # Base score calculation
        if matching_skills:
            skill_match_score = min(len(matching_skills) * 10, 70)
        else:
            skill_match_score = 15  # Base score for relevant profession
        
        # Calculate experience match (30 points max)
        experience_level = getattr(self.resume, 'experience_level', '') or ''
        experience_level = experience_level.lower() if experience_level else ''
        
        job_title = job_data.get('name', '') or ''
        job_title = job_title.lower() if job_title else ''
        
        job_requirements = ''
        if job_data and job_data.get('snippet') and job_data.get('snippet').get('requirement'):
            job_requirements = str(job_data.get('snippet').get('requirement')).lower()
        
        experience_match_score = self._calculate_experience_match(experience_level, job_title, job_requirements)
        
        # Total score (100 possible points)
        total_score = skill_match_score + experience_match_score
        
        # Detail what contributed to the score
        match_details = {
            'skill_score': skill_match_score,
            'experience_score': experience_match_score,
            'matching_skills': list(matching_skills),
            'missing_skills': list(missing_skills)
        }
        
        return total_score, match_details
    
    def _calculate_experience_match(self, experience_level: str, job_title: str, job_requirements: str) -> float:
        """
        Calculate experience level match score for any profession
        """
        # Universal experience keywords
        senior_keywords = ['senior', 'lead', 'sr', 'principal', 'chief', 'head', 'director', 'manager']
        middle_keywords = ['middle', 'mid', 'mid-level', 'experienced', 'specialist']
        junior_keywords = ['junior', 'entry', 'jr', 'assistant', 'associate', 'trainee', 'intern']
        
        # Ensure all inputs are strings
        experience_level = str(experience_level) if experience_level else ''
        job_title = str(job_title) if job_title else ''
        job_requirements = str(job_requirements) if job_requirements else ''
        
        # Check for experience match
        if experience_level == 'senior' and any(keyword in job_title or keyword in job_requirements 
                                              for keyword in senior_keywords):
            return 30
        elif experience_level == 'middle' and any(keyword in job_title or keyword in job_requirements 
                                                for keyword in middle_keywords):
            return 30
        elif experience_level == 'junior' and any(keyword in job_title or keyword in job_requirements 
                                               for keyword in junior_keywords):
            return 30
        else:
            # Default partial match for reasonable fit
            return 15

    def find_matching_jobs(self, search_query: Optional[str] = None, 
                          location: Optional[str] = None) -> List[Tuple[Job, float, Dict[str, Any]]]:
        """
        Find, analyze and score jobs that match the resume across all professions
        
        Args:
            search_query: Job search query (if None, will generate from resume)
            location: Location string to search in (if None, will use default)
            
        Returns:
            List of (Job, match_score, match_details) tuples, sorted by match score
        """
        # Generate search query if not provided
        if not search_query:
            search_query = self.generate_search_query_from_resume()
        
        # Fetch job listings
        job_items = self.fetch_relevant_jobs(search_query, location)
        
        # Process and score each job
        job_matches = []
        for item in job_items:
            try:
                # Create or get Job object
                # Ensure all required fields have default values
                if 'id' not in item:
                    logger.warning("Skipping job item without ID: %s", str(item)[:100])
                    continue
                    
                # Handle required fields with appropriate defaults
                job_data = {
                    'title': item.get('name', 'Untitled Job'),
                    'company_name': item.get('employer', {}).get('name', 'Unknown Company') if item.get('employer') else 'Unknown Company',
                    'company_url': item.get('employer', {}).get('alternate_url', '') if item.get('employer') else '',
                    'description': item.get('snippet', {}).get('responsibility', '') if item.get('snippet') else '',
                    'requirements': item.get('snippet', {}).get('requirement') or '' if item.get('snippet') else '',
                    'salary_from': item.get('salary', {}).get('from') if item.get('salary') else None,
                    'salary_to': item.get('salary', {}).get('to') if item.get('salary') else None,
                    'salary_currency': item.get('salary', {}).get('currency', 'RUB') if item.get('salary') else 'RUB',
                    'location': item.get('area', {}).get('name', '') if item.get('area') else '',
                    'employment_type': item.get('employment', {}).get('name', '') if item.get('employment') else '',
                    'hh_url': item.get('alternate_url', ''),
                    'published_at': item.get('published_at', timezone.now()),
                    'is_active': True
                }
                
                job, created = Job.objects.get_or_create(
                    hh_id=item['id'],
                    defaults=job_data
                )
            except Exception as e:
                logger.error("Error processing job item: %s", str(e))
                continue
            
            # If job is new, fetch more details using vacancy_id
            if created and item.get('id'):
                try:
                    details = self.api_client.get_vacancy_details(item['id'])
                    job.description = details.get('description', job.description)
                    # Update skills list based on detailed description
                    job.save()
                except Exception as e:
                    logger.warning("Failed to fetch details for job %s: %s", item['id'], str(e))
            
            # Calculate match score
            match_score, match_details = self.calculate_match_score(item)
            
            # Save match details
            if self.resume:
                JobMatch.objects.update_or_create(
                    job=job,
                    resume=self.resume,
                    defaults={
                        'user': self.user,
                        'match_score': match_score,
                        'match_details': match_details,
                        'matching_skills': match_details.get('matching_skills', []),
                        'missing_skills': match_details.get('missing_skills', [])
                    }
                )
            
            job_matches.append((job, match_score, match_details))
        
        # Sort by match score (descending)
        job_matches.sort(key=lambda x: x[1], reverse=True)
        
        return job_matches
