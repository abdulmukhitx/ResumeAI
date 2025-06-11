"""
AI-powered job matching functionality to find the best job opportunities
based on skills, experience, and education from uploaded resumes.
"""

import logging
import re
from typing import List, Dict, Any, Tuple, Optional, Set
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from .services import HHApiClient

# Get models dynamically to avoid circular imports
Resume = apps.get_model('resumes', 'Resume')
Job = apps.get_model('jobs', 'Job')
JobMatch = apps.get_model('jobs', 'JobMatch')
JobSearch = apps.get_model('jobs', 'JobSearch')

logger = logging.getLogger(__name__)

class JobMatcher:
    """
    AI-powered job matching functionality that:
    - Uses analyzed resume data to find best job opportunities
    - Retrieves relevant jobs from HH.ru API
    - Ranks and presents jobs based on match score
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
            logger.error(f"Error fetching jobs: {str(e)}")
            return []
    
    def generate_search_query_from_resume(self) -> str:
        """
        Generate an optimal search query based on resume data
        """
        if not self.resume:
            return ""
            
        # Extract key information from resume
        job_titles = self.resume.job_titles
        skills = self.resume.extracted_skills
        
        # Start with the most recent job title or a relevant skill
        if job_titles and len(job_titles) > 0:
            primary_term = job_titles[0]
        elif skills and len(skills) > 0:
            # Use the first 1-2 skills as primary search term
            primary_term = ' '.join(skills[:2])
        else:
            primary_term = ""
            
        # If we don't have any data to work with, use a generic term
        if not primary_term:
            return "developer"
            
        return primary_term
    
    def _extract_skills_from_job(self, job_data: Dict[str, Any]) -> Set[str]:
        """
        Extract skills from job description and requirements
        
        Args:
            job_data: Job dictionary containing description and requirements
        
        Returns:
            Set of extracted skills
        """
        if not job_data:
            return set()
            
        # Safely get nested dict values
        snippet_req = job_data.get('snippet', {}).get('requirement', '') if job_data.get('snippet') else ''
        snippet_resp = job_data.get('snippet', {}).get('responsibility', '') if job_data.get('snippet') else ''
        
        # Combine description and requirements
        full_text = ' '.join([
            job_data.get('description', ''),
            job_data.get('requirements', ''),
            snippet_req,
            snippet_resp
        ]).lower()
        
        # Common tech skills to look for
        tech_skills = [
            "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "ruby", "php", "swift", "kotlin",
            "html", "css", "sass", "less", "tailwind", "bootstrap", "sql", "nosql", "mongodb", "postgresql", 
            "mysql", "oracle", "redis", "react", "angular", "vue", "svelte", "jquery", "redux", "gatsby", "nextjs",
            "django", "laravel", "flask", "rails", "express", "spring", "node", "deno", "asp\\.net",
            "docker", "kubernetes", "aws", "azure", "gcp", "firebase", "heroku", "netlify", "vercel",
            "git", "github", "gitlab", "bitbucket", "jenkins", "travis", "circle", "ansible", "terraform"
        ]
        
        # Extract skills using regex with word boundaries
        skills = set()
        for skill in tech_skills:
            pattern = r'\b' + skill.replace('.', '[ -]?') + r'\b'
            if re.search(pattern, full_text):
                skills.add(skill.replace('\\', '').replace('.', ' '))
                
        return skills
    
    def calculate_match_score(self, job_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate match score between resume and job
        
        Args:
            job_data: Job dictionary with title, description, requirements, etc.
        
        Returns:
            Tuple of (match_score, match_details)
        """
        if not self.resume:
            return 0.0, {}
        
        # Extract job skills
        job_skills = self._extract_skills_from_job(job_data)
        
        # Get resume skills
        resume_skills = set(self.resume.extracted_skills)
        
        # Calculate skill match
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills
        skill_match_score = len(matching_skills) * 10
        
        # If no skills match, give a low base score
        if not matching_skills:
            skill_match_score = 15
            
        # Cap skill score at 70 points
        skill_match_score = min(skill_match_score, 70)
        
        # Calculate experience match (30 points max)
        experience_level = getattr(self.resume, 'experience_level', '').lower() if self.resume else ''
        job_title = job_data.get('name', '').lower() if job_data else ''
        job_requirements = job_data.get('snippet', {}).get('requirement', '').lower() if job_data and job_data.get('snippet') else ''
        
        experience_match_score = 0
        
        # Simple seniority keyword matching
        if experience_level == 'senior' and any(keyword in job_title or keyword in job_requirements 
                                              for keyword in ['senior', 'lead', 'sr', 'principal']):
            experience_match_score = 30
        elif experience_level == 'middle' and any(keyword in job_title or keyword in job_requirements 
                                                for keyword in ['middle', 'mid', 'mid-level']):
            experience_match_score = 30
        elif experience_level == 'junior' and any(keyword in job_title or keyword in job_requirements 
                                               for keyword in ['junior', 'entry', 'jr']):
            experience_match_score = 30
        else:
            # Default partial match
            experience_match_score = 15
            
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
    
    def find_matching_jobs(self, search_query: Optional[str] = None, 
                          location: Optional[str] = None) -> List[Tuple[Job, float, Dict[str, Any]]]:
        """
        Find, analyze and score jobs that match the resume
        
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
                    logger.warning(f"Skipping job item without ID: {str(item)[:100]}...")
                    continue
                    
                # Handle required fields with appropriate defaults
                job_data = {
                    'title': item.get('name', 'Untitled Job'),
                    'company_name': item.get('employer', {}).get('name', 'Unknown Company') if item.get('employer') else 'Unknown Company',
                    'company_url': item.get('employer', {}).get('alternate_url', '') if item.get('employer') else '',
                    'description': item.get('snippet', {}).get('responsibility', '') if item.get('snippet') else '',
                    'requirements': item.get('snippet', {}).get('requirement', '') if item.get('snippet') else '',
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
                logger.error(f"Error processing job item: {str(e)}")
                continue
            
            # If job is new, fetch more details using vacancy_id
            if created and item.get('id'):
                try:
                    details = self.api_client.get_vacancy_details(item['id'])
                    job.description = details.get('description', job.description)
                    # Update skills list based on detailed description
                    job.save()
                except Exception as e:
                    logger.warning(f"Failed to fetch details for job {item['id']}: {str(e)}")
            
            # Calculate match score
            match_score, match_details = self.calculate_match_score(item)
            
            # Save match details
            if self.resume:
                job_match, created = JobMatch.objects.update_or_create(
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
