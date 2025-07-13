import requests
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

class EnhancedHHApiClient:
    """Enhanced HH API client that fetches jobs from both HH.ru and HH.kz"""
    
    # HH.ru API endpoints
    HH_RU_BASE_URL = "https://api.hh.ru"
    HH_KZ_BASE_URL = "https://api.hh.kz"
    
    # Extended location mapping for both countries
    LOCATION_MAPPING = {
        # Kazakhstan locations
        'almaty': '160',
        'nur-sultan': '159',
        'astana': '159',
        'shymkent': '202',
        'karaganda': '161',
        'aktau': '182',
        'atyrau': '181',
        'kazakhstan': '40',
        'kz': '40',
        
        # Russia locations
        'moscow': '1',
        'saint petersburg': '2',
        'st petersburg': '2',
        'russia': '113',
        'ru': '113',
        'novosibirsk': '4',
        'yekaterinburg': '3',
        
        # Common locations
        'remote': '1221',
        'worldwide': '1001',
    }
    
    def __init__(self):
        self.user_agent = "ResumeAI/1.0 (contact@resumeai.com)"
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.timeout = 30
    
    def _resolve_location(self, location: Optional[Union[str, int]]) -> Optional[str]:
        """Resolve location string or ID to valid HH area ID"""
        if location is None:
            return '1'  # Default to Moscow
            
        if isinstance(location, int) or (isinstance(location, str) and str(location).isdigit()):
            return str(location)
            
        if isinstance(location, str):
            location = location.lower().strip()
            
            # Handle comma-separated values
            if ',' in location:
                location_parts = [part.strip() for part in location.split(',')]
                
                for part in location_parts:
                    if part in self.LOCATION_MAPPING:
                        return self.LOCATION_MAPPING[part]
            
            # Direct lookup
            if location in self.LOCATION_MAPPING:
                return self.LOCATION_MAPPING[location]
        
        logger.info(f"Could not resolve location '{location}', defaulting to Moscow")
        return '1'
    
    def _generate_search_params(self, search_query: str = None, location: str = None, 
                              per_page: int = 20, experience: str = None) -> Dict[str, Any]:
        """Generate search parameters for HH API"""
        params = {
            'per_page': min(per_page, 100),  # HH API max is 100
            'page': 0,
            'order_by': 'publication_time',  # Use valid order_by value
            'enable_snippets': 'true',
        }
        
        if search_query:
            params['text'] = search_query
        
        if location:
            params['area'] = self._resolve_location(location)
        
        if experience:
            # Map experience levels to HH API values
            experience_mapping = {
                'junior': 'noExperience',
                'middle': 'between1And3',
                'senior': 'between3And6',
                'lead': 'moreThan6',
            }
            params['experience'] = experience_mapping.get(experience.lower(), 'noExperience')
        
        return params
    
    def _fetch_from_single_api(self, base_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch jobs from a single HH API endpoint"""
        url = f"{base_url}/vacancies"
        
        try:
            logger.info(f"Fetching from {base_url} with params: {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('items', []))} jobs from {base_url}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch from {base_url}: {str(e)}")
            return {'items': [], 'found': 0, 'pages': 0}
    
    def fetch_jobs_from_both_apis(self, search_query: str = None, location: str = None, 
                                 per_page: int = 50) -> List[Dict[str, Any]]:
        """Fetch jobs from both HH.ru and HH.kz APIs"""
        
        # Generate search parameters
        params = self._generate_search_params(search_query, location, per_page // 2)
        
        # Fetch from both APIs concurrently
        all_jobs = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks for both APIs
            future_ru = executor.submit(self._fetch_from_single_api, self.HH_RU_BASE_URL, params)
            future_kz = executor.submit(self._fetch_from_single_api, self.HH_KZ_BASE_URL, params)
            
            # Get results
            ru_data = future_ru.result()
            kz_data = future_kz.result()
            
            # Combine results
            all_jobs.extend(ru_data.get('items', []))
            all_jobs.extend(kz_data.get('items', []))
        
        # Remove duplicates based on job ID
        seen_ids = set()
        unique_jobs = []
        
        for job in all_jobs:
            job_id = job.get('id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        logger.info(f"Fetched {len(unique_jobs)} unique jobs from both APIs")
        return unique_jobs
    
    def get_job_details(self, job_id: str, base_url: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific job"""
        if base_url is None:
            base_url = self.HH_RU_BASE_URL
            
        url = f"{base_url}/vacancies/{job_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch job details for {job_id}: {str(e)}")
            return {}
    
    def search_jobs_for_resume(self, resume_text: str, skills: List[str], 
                              location: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs that match a resume's skills and content"""
        
        # Generate search query from skills
        search_queries = []
        
        if skills:
            # Use top skills as search terms (simpler approach)
            tech_skills = [skill for skill in skills if self._is_tech_skill(skill)]
            if tech_skills:
                # Use individual skills instead of OR operator
                search_queries.extend(tech_skills[:3])
            
            # Add general skill search
            general_skills = [skill for skill in skills if not self._is_tech_skill(skill)]
            if general_skills:
                search_queries.extend(general_skills[:2])
        
        # If no skills, use generic tech terms
        if not search_queries:
            search_queries = ['developer', 'engineer', 'programmer', 'analyst', 'manager']
        
        all_jobs = []
        
        # Search with different queries to get diverse results
        for query in search_queries[:3]:  # Limit to 3 queries
            try:
                jobs = self.fetch_jobs_from_both_apis(
                    search_query=query,
                    location=location,
                    per_page=limit // len(search_queries[:3])
                )
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error searching with query '{query}': {str(e)}")
                continue
        
        # If no jobs found, try a general search without specific terms
        if not all_jobs:
            try:
                jobs = self.fetch_jobs_from_both_apis(
                    search_query=None,  # Get general jobs
                    location=location,
                    per_page=limit
                )
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error in general search: {str(e)}")
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_jobs = []
        
        for job in all_jobs:
            job_id = job.get('id')
            if job_id and job_id not in seen_ids and len(unique_jobs) < limit:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        logger.info(f"Found {len(unique_jobs)} unique jobs matching resume")
        return unique_jobs
    
    def _is_tech_skill(self, skill: str) -> bool:
        """Check if a skill is technology-related"""
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'sql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux',
            'html', 'css', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'golang', 'rust', 'scala', 'kotlin', 'swift', 'android',
            'ios', 'flutter', 'tensorflow', 'pytorch', 'machine learning',
            'data science', 'devops', 'cloud', 'api', 'rest', 'graphql'
        ]
        
        return any(keyword in skill.lower() for keyword in tech_keywords)


class RealTimeJobMatcher:
    """Real-time job matching using HH APIs"""
    
    def __init__(self, user, resume):
        self.user = user
        self.resume = resume
        self.hh_client = EnhancedHHApiClient()
    
    def calculate_match_score(self, job_data: Dict[str, Any], user_skills: List[str]) -> Dict[str, Any]:
        """Calculate match score between job and user skills"""
        
        # Extract job text for matching
        job_text = f"{job_data.get('name', '')} {job_data.get('snippet', {}).get('requirement', '')} {job_data.get('snippet', {}).get('responsibility', '')}"
        job_text = job_text.lower()
        
        # Find matching skills
        matching_skills = []
        for skill in user_skills:
            if skill.lower() in job_text:
                matching_skills.append(skill)
        
        # Calculate base match score
        if not user_skills:
            match_score = 25
        else:
            match_score = (len(matching_skills) / len(user_skills)) * 100
        
        # Boost score for tech jobs if user has tech skills
        tech_skills = [skill for skill in user_skills if self._is_tech_skill(skill)]
        if tech_skills:
            tech_keywords = ['developer', 'engineer', 'programmer', 'analyst', 'architect', 'technical']
            job_title = job_data.get('name', '').lower()
            
            if any(keyword in job_title for keyword in tech_keywords):
                match_score = min(match_score * 1.5, 100)  # Boost tech jobs
        
        # Ensure minimum score
        match_score = max(match_score, 5)
        
        return {
            'match_score': round(match_score, 1),
            'matching_skills': matching_skills,
            'missing_skills': [skill for skill in user_skills if skill not in matching_skills]
        }
    
    def _is_tech_skill(self, skill: str) -> bool:
        """Check if a skill is technology-related"""
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'sql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux',
            'html', 'css', 'typescript', 'c++', 'c#', 'php', 'ruby'
        ]
        return any(keyword in skill.lower() for keyword in tech_keywords)
    
    def find_matching_jobs(self, search_query: str = None, location: str = None, 
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Find jobs that match the user's resume in real-time"""
        
        # Get user skills
        user_skills = []
        if hasattr(self.resume, 'extracted_skills') and self.resume.extracted_skills:
            user_skills = self.resume.extracted_skills
        
        # Search for jobs using HH APIs
        if search_query:
            # Use provided search query
            jobs = self.hh_client.fetch_jobs_from_both_apis(
                search_query=search_query,
                location=location,
                per_page=limit
            )
        else:
            # Generate search based on resume skills
            jobs = self.hh_client.search_jobs_for_resume(
                resume_text=getattr(self.resume, 'content', ''),
                skills=user_skills,
                location=location,
                limit=limit
            )
        
        # Calculate match scores and create job objects
        matched_jobs = []
        
        for job_data in jobs:
            try:
                # Calculate match score
                match_info = self.calculate_match_score(job_data, user_skills)
                
                # Create job object (temporary, not saved to database)
                job_obj = self._create_job_object(job_data, match_info)
                matched_jobs.append(job_obj)
                
            except Exception as e:
                logger.error(f"Error processing job {job_data.get('id', 'unknown')}: {str(e)}")
                continue
        
        # Sort by match score (descending)
        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"Successfully matched {len(matched_jobs)} jobs")
        return matched_jobs
    
    def _create_job_object(self, job_data: Dict[str, Any], match_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a job object from HH API data"""
        
        # Extract salary information
        salary = job_data.get('salary', {})
        salary_from = salary.get('from') if salary else None
        salary_to = salary.get('to') if salary else None
        salary_currency = salary.get('currency') if salary else None
        
        # Extract location
        area = job_data.get('area', {})
        location = area.get('name') if area else 'Not specified'
        
        # Extract company
        employer = job_data.get('employer', {})
        company_name = employer.get('name') if employer else 'Not specified'
        
        # Extract employment type
        employment = job_data.get('employment', {})
        employment_type = employment.get('name') if employment else None
        
        # Extract experience
        experience = job_data.get('experience', {})
        experience_required = experience.get('name') if experience else None
        
        # Extract snippet (description)
        snippet = job_data.get('snippet', {})
        description = f"{snippet.get('requirement', '')} {snippet.get('responsibility', '')}".strip()
        
        return {
            'id': job_data.get('id'),
            'title': job_data.get('name', 'Untitled Job'),
            'company_name': company_name,
            'location': location,
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_currency': salary_currency,
            'employment_type': employment_type,
            'experience_required': experience_required,
            'description': description,
            'hh_url': job_data.get('alternate_url'),
            'created_at': job_data.get('created_at'),
            'published_at': job_data.get('published_at'),
            
            # Match information
            'match_score': match_info['match_score'],
            'matching_skills': match_info['matching_skills'],
            'missing_skills': match_info['missing_skills'],
        }
