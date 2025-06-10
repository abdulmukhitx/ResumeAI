import PyPDF2
import requests
from django.conf import settings
from typing import Dict, Any

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}") from e

class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = settings.GROQ_API_URL
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PDFProcessor"""
        return PDFProcessor.extract_text_from_pdf(file_path)
        
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using Groq AI"""
        # Import modules needed for parsing
        import json
        import re
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check if API key is properly configured - silently use fallback if not
        if not self.api_key or self.api_key == 'your-groq-api-key':
            logger.info("Using local resume analysis (AI not configured)")
            return self._fallback_analysis(resume_text, "AI analysis not enabled")
        
        prompt = f"""
        Analyze the following resume and extract structured information in JSON format:

        Resume Text:
        {resume_text}

        Please extract and return ONLY a valid JSON object with these fields:
        {{
            "skills": ["list of technical and soft skills"],
            "experience_level": "entry/junior/middle/senior/lead",
            "job_titles": ["list of job titles from work experience"],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school/university name",
                    "year": "graduation year or period"
                }}
            ],
            "work_experience": [
                {{
                    "position": "job title",
                    "company": "company name",
                    "duration": "time period",
                    "key_responsibilities": ["main responsibilities"]
                }}
            ],
            "summary": "A brief professional summary based on the resume content",
            "confidence_score": 0.95
        }}

        Guidelines:
        - Extract only information that is clearly stated in the resume
        - For experience_level, consider years of experience and seniority of positions
        - Skills should include both technical skills and relevant soft skills
        - If information is not available, use empty arrays or null values
        - Confidence score should be between 0.0 and 1.0 based on text quality

        Only return the JSON object, no explanations or other text.
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        # Select appropriate model based on key validity
        model = 'llama3-8b-8192' if not self.api_key.startswith('gsk_') else 'llama3-70b-8192'
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert resume analyzer. Extract structured information from resumes accurately.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,  # Low temperature for more deterministic outputs
            'max_tokens': 2000
        }
        
        ai_response = ""
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            # Try to find JSON block in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                # Extract JSON from code block
                json_str = json_match.group(1)
            else:
                # Assume the entire response is JSON
                json_str = ai_response
                
            # Clean up and parse JSON
            json_str = re.sub(r'```|json', '', json_str).strip()
            parsed_data = json.loads(json_str)
            
            # Log successful analysis
            logger.info(f"Resume analysis successful with confidence score: {parsed_data.get('confidence_score', 0.0)}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from the response
            try:
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    return analysis_data
            except Exception:
                pass
                
            # Log error and use fallback analysis
            logger.error(f"Error parsing JSON from AI response: {str(e)}")
            return self._fallback_analysis(resume_text)
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API request failed with HTTP error: {str(e)}")
            
            # Check if we're having authentication problems
            if e.response.status_code == 401:
                logger.error("Authentication error. Check your API key.")
            
            # Don't expose API error codes to users
            return self._fallback_analysis(resume_text)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AI API request failed: {str(e)}")
            return self._fallback_analysis(resume_text)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis(resume_text)
    
    def _fallback_analysis(self, resume_text: str, reason: str = None) -> Dict[str, Any]:
        """Enhanced local resume analysis when AI is unavailable"""
        import re
        
        # Expanded skills extraction using regex patterns
        tech_skills = [
            "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "ruby", "php", "swift", "kotlin",
            "html", "css", "sass", "less", "tailwind", "bootstrap", "sql", "nosql", "mongodb", "postgresql", 
            "mysql", "oracle", "redis", "react", "angular", "vue", "svelte", "jquery", "redux", "gatsby", "nextjs",
            "django", "laravel", "flask", "rails", "express", "spring", "node", "deno", "asp\\.net",
            "docker", "kubernetes", "aws", "azure", "gcp", "firebase", "heroku", "netlify", "vercel",
            "git", "github", "gitlab", "bitbucket", "jenkins", "travis", "circle", "ansible", "terraform"
        ]
        
        soft_skills = [
            "leadership", "communication", "teamwork", "problem.solving", "critical.thinking",
            "time.management", "decision.making", "organization", "agile", "scrum", "kanban",
            "presentation", "negotiation", "conflict.resolution", "mentoring", "coaching"
        ]
        
        # Extract skills using regex with word boundaries
        skills = []
        for skill in tech_skills + soft_skills:
            pattern = r'\b' + skill.replace('.', '[ -]?') + r'\b'
            if re.search(pattern, resume_text.lower()):
                skills.append(skill.replace('\\', '').replace('.', ' '))
        
        # Enhanced experience level estimation
        experience_level = "junior"  # Default
        text_lower = resume_text.lower()
        
        # Look for years of experience
        year_patterns = [
            (r'(\d+)\+?\s*years?\s*(?:of)?\s*experience', lambda x: int(x) if x else 0),
            (r'experience\s*(?:of|:)?\s*(\d+)\+?\s*years?', lambda x: int(x) if x else 0)
        ]
        
        years = 0
        for pattern, extract in year_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = max([extract(m) for m in matches] + [years])
        
        if years > 8 or re.search(r'senior|lead|director|head|chief|principal|vp|vice president', text_lower):
            experience_level = "senior"
        elif years > 3 or re.search(r'middle|mid-level|intermediate|mid senior', text_lower):
            experience_level = "middle"
        elif years > 0 or re.search(r'junior|entry|intern|graduate', text_lower):
            experience_level = "junior"
        
        # Better job title extraction
        job_titles = []
        title_patterns = [
            r'(senior|lead|principal|staff)?\s*(software|frontend|backend|full[\s-]?stack|mobile|ios|android|web|cloud|data|devops|ml|ai|system|network|security)\s*(developer|engineer|architect)',
            r'(ux|ui|user experience|user interface|product|project|program|technical|engineering|it|information technology)\s*(designer|manager|lead|director)',
            r'(data|business|systems|financial|marketing|sales)\s*(analyst|scientist)',
            r'(scrum|agile|product|project|program|delivery)\s*(master|manager|owner|lead|coach)'
        ]
        
        # Extract multiple job titles
        for pattern in title_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):  # Multiple capture groups
                    title = ' '.join(part for part in match if part).strip()
                else:  # Single capture group
                    title = match.strip()
                if title and title not in job_titles:
                    job_titles.append(title.title())  # Convert to title case
        
        # If no specific titles found, look for generic job titles
        if not job_titles:
            generic_matches = re.findall(r'(Developer|Engineer|Designer|Manager|Analyst|Consultant|Director|Lead)[^,\n]*', resume_text)
            if generic_matches:
                job_titles = [title.strip() for title in generic_matches[:3]]  # Take top 3 matches
        
        # Extract education - look for common degree patterns
        education = []
        degree_patterns = [
            (r'(bachelor|master|phd|doctorate|bs|ba|ms|ma|mba|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|m\.?b\.?a\.?|ph\.?d\.?)[^\n,]*?(?:in|of)?[^\n,]*?(engineering|science|arts|business|computer|information|technology|mathematics|physics|chemistry|biology)[^\n]*?(\d{4})?', 
             lambda m: {"degree": m[0].strip(), "institution": "", "year": m[2] if len(m) > 2 and m[2] else ""})
        ]
        
        for pattern, extract in degree_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                edu_entry = extract(match)
                if edu_entry and edu_entry not in education:
                    education.append(edu_entry)
        
        # Create a reasonable summary
        summary = "Resume processed using advanced text analysis"
        if reason and "not enabled" not in reason:
            summary += f" ({reason})"
        
        return {
            "skills": skills,
            "experience_level": experience_level,
            "job_titles": job_titles,
            "education": education,
            "work_experience": [],  # Complex to extract reliably without AI
            "summary": summary,
            "confidence_score": 0.5  # Medium confidence for enhanced local analysis
        }