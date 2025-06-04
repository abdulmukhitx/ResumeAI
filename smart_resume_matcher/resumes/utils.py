import PyPDF2
import requests
from io import BytesIO
from django.conf import settings
from typing import Dict, List, Any

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
            raise Exception(f"Error extracting text from PDF: {str(e)}")

class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = settings.GROQ_API_URL
        
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume using Groq AI"""
        
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
            "summary": "Brief professional summary in 2-3 sentences",
            "confidence_score": 0.85
        }}

        Guidelines:
        - Extract only information that is clearly stated in the resume
        - For experience_level, consider years of experience and seniority of positions
        - Skills should include both technical skills and relevant soft skills
        - If information is not available, use empty arrays or null values
        - Confidence score should be between 0.0 and 1.0 based on text quality
        """
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'llama3-8b-8192',  # Groq's free model
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert resume analyzer. Always return valid JSON format only, no additional text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 1500,
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON from the response
            import json
            try:
                analysis_data = json.loads(content)
                return analysis_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    return analysis_data
                else:
                    raise Exception("Could not parse JSON from AI response")
                    
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")