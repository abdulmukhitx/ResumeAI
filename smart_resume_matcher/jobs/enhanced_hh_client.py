"""
Enhanced HH API Client for fetching jobs from HH.ru and HH.kz
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JobData:
    """Data class to represent a job from HH API"""
    id: str
    title: str
    company: str
    location: str
    salary_from: Optional[float]
    salary_to: Optional[float]
    salary_currency: str
    description: str
    requirements: str
    url: str
    employment_type: str
    experience_required: str
    source: str  # 'hh.ru' or 'hh.kz'
    skills: List[str]
    published_at: str

class EnhancedHHApiClient:
    """Enhanced HH API client for real-time job fetching"""
    
    # HH.ru and HH.kz endpoints
    HH_RU_BASE = "https://api.hh.ru"
    HH_KZ_BASE = "https://api.hh.kz"
    
    # Location mappings for both countries
    LOCATION_MAPPING = {
        # Kazakhstan cities
        'almaty': '160',
        'nur-sultan': '159',
        'astana': '159',
        'shymkent': '202',
        'karaganda': '161',
        'aktau': '182',
        'atyrau': '181',
        'kazakhstan': '40',
        
        # Russia cities
        'moscow': '1',
        'saint petersburg': '2',
        'st petersburg': '2',
        'russia': '113',
        'novosibirsk': '4',
        'yekaterinburg': '3',
        
        # Remote work
        'remote': '1002',
        'удаленно': '1002',
    }
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'SmartResumeMatcherApp/1.0 (contact@resumematcher.com)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
    def _resolve_location(self, location: Optional[str]) -> str:
        """Resolve location string to HH area ID"""
        if not location:
            return '1'  # Default to Moscow
            
        location = location.lower().strip()
        
        # Handle comma-separated values
        if ',' in location:
            location_parts = [part.strip() for part in location.split(',')]
            for part in location_parts:
                if part in self.LOCATION_MAPPING:
                    return self.LOCATION_MAPPING[part]
        
        # Direct lookup
        return self.LOCATION_MAPPING.get(location, '1')
    
    def _extract_skills_from_job(self, job_data: Dict) -> List[str]:
        """Extract skills from job description and requirements"""
        skills = []
        
        # Common tech skills to look for
        tech_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'django',
            'flask', 'node.js', 'php', 'laravel', 'c++', 'c#', 'ruby', 'go',
            'swift', 'kotlin', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'linux',
            'typescript', 'html', 'css', 'sass', 'less', 'webpack', 'babel',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'ci/cd',
            'машинное обучение', 'data science', 'ai', 'ml', 'tensorflow', 'pytorch'
        ]
        
        # Get text from job
        text_fields = []
        if job_data.get('description'):
            text_fields.append(job_data['description'])
        if job_data.get('requirement'):
            text_fields.append(job_data['requirement'])
        if job_data.get('responsibility'):
            text_fields.append(job_data['responsibility'])
        
        combined_text = ' '.join(text_fields).lower()
        
        # Find matching skills
        for skill in tech_skills:
            if skill in combined_text:
                skills.append(skill.title())
        
        return list(set(skills))
    
    def _parse_job_data(self, job_data: Dict, source: str) -> JobData:
        """Parse job data from HH API response"""
        # Extract salary info
        salary_info = job_data.get('salary', {})
        salary_from = salary_info.get('from') if salary_info else None
        salary_to = salary_info.get('to') if salary_info else None
        salary_currency = salary_info.get('currency', 'RUB') if salary_info else 'RUB'
        
        # Extract employer info
        employer = job_data.get('employer', {})
        company_name = employer.get('name', 'Company not specified')
        
        # Extract area info
        area = job_data.get('area', {})
        location = area.get('name', 'Location not specified')
        
        # Extract employment type
        employment = job_data.get('employment', {})
        employment_type = employment.get('name', 'Full-time')
        
        # Extract experience requirement
        experience = job_data.get('experience', {})
        experience_required = experience.get('name', 'Not specified')
        
        # Extract skills
        skills = self._extract_skills_from_job(job_data)
        
        return JobData(
            id=str(job_data.get('id')),
            title=job_data.get('name', 'Job Title Not Available'),
            company=company_name,
            location=location,
            salary_from=salary_from,
            salary_to=salary_to,
            salary_currency=salary_currency,
            description=job_data.get('snippet', {}).get('responsibility', ''),
            requirements=job_data.get('snippet', {}).get('requirement', ''),
            url=job_data.get('alternate_url', ''),
            employment_type=employment_type,
            experience_required=experience_required,
            source=source,
            skills=skills,
            published_at=job_data.get('published_at', '')
        )
    
    def _fetch_jobs_from_api(self, base_url: str, params: Dict, source: str) -> List[JobData]:
        """Fetch jobs from a specific HH API endpoint"""
        try:
            url = f"{base_url}/vacancies"
            logger.info(f"Fetching jobs from {source} with params: {params}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            jobs = []
            
            for job_data in data.get('items', []):
                try:
                    job = self._parse_job_data(job_data, source)
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"Failed to parse job {job_data.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(jobs)} jobs from {source}")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request to {source} failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing jobs from {source}: {e}")
            return []
    
    def search_jobs_realtime(self, search_query: str = '', location: str = '', 
                           per_page: int = 50, max_total: int = 100) -> List[JobData]:
        """
        Fetch fresh jobs from both HH.ru and HH.kz APIs in real-time
        """
        logger.info(f"Starting real-time job search: query='{search_query}', location='{location}'")
        
        # Resolve location
        area_id = self._resolve_location(location)
        
        # Base search parameters
        base_params = {
            'text': search_query,
            'area': area_id,
            'per_page': min(per_page, 100),  # HH API limit
            'only_with_salary': 'false',
            'order_by': 'relevance',
            'search_field': 'name,company_name,description'
        }
        
        # Prepare parameters for both APIs
        ru_params = base_params.copy()
        kz_params = base_params.copy()
        
        all_jobs = []
        
        # Fetch from both APIs concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks for both APIs
            future_ru = executor.submit(
                self._fetch_jobs_from_api, 
                self.HH_RU_BASE, 
                ru_params, 
                'hh.ru'
            )
            future_kz = executor.submit(
                self._fetch_jobs_from_api, 
                self.HH_KZ_BASE, 
                kz_params, 
                'hh.kz'
            )
            
            # Collect results
            for future in as_completed([future_ru, future_kz]):
                try:
                    jobs = future.result()
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Error fetching jobs: {e}")
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            job_key = (job.title.lower(), job.company.lower())
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        # Sort by relevance (jobs with more skills first)
        unique_jobs.sort(key=lambda x: len(x.skills), reverse=True)
        
        # Limit results
        final_jobs = unique_jobs[:max_total]
        
        logger.info(f"Real-time search completed: {len(final_jobs)} unique jobs found")
        return final_jobs
    
    def get_job_details(self, job_id: str, source: str = 'hh.ru') -> Optional[Dict]:
        """Get detailed information about a specific job"""
        base_url = self.HH_RU_BASE if source == 'hh.ru' else self.HH_KZ_BASE
        
        try:
            url = f"{base_url}/vacancies/{job_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get job details for {job_id}: {e}")
            return None
    
    def generate_search_query_from_skills(self, skills: List[str]) -> str:
        """Generate search query from user skills"""
        if not skills:
            return 'developer'
        
        # Prioritize tech skills
        tech_skills = []
        other_skills = []
        
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'django',
            'flask', 'node', 'php', 'laravel', 'c++', 'c#', 'ruby', 'go',
            'swift', 'kotlin', 'sql', 'mysql', 'postgresql', 'mongodb'
        ]
        
        for skill in skills:
            if any(tech in skill.lower() for tech in tech_keywords):
                tech_skills.append(skill)
            else:
                other_skills.append(skill)
        
        # Build search query
        if tech_skills:
            # Use primary tech skill
            primary_skill = tech_skills[0]
            if 'python' in primary_skill.lower():
                return 'python developer'
            elif 'java' in primary_skill.lower():
                return 'java developer'
            elif 'javascript' in primary_skill.lower() or 'react' in primary_skill.lower():
                return 'frontend developer'
            else:
                return f'{primary_skill} developer'
        
        # Fallback to general terms
        return 'developer programmer'
