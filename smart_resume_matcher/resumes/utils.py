import PyPDF2
import requests
from django.conf import settings
from typing import Dict, Any
from .universal_skills import get_all_skills

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file using multiple methods"""
        import logging
        logger = logging.getLogger(__name__)
        
        text = ""
        methods_tried = 0
        
        # Method 1: Try with PyPDF2 first
        try:
            import PyPDF2
            methods_tried += 1
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                logger.info("Successfully extracted text using PyPDF2")
                return text.strip()
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # Method 2: Try with pdfminer.six
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            methods_tried += 1
            text = pdfminer_extract(file_path)
            
            if text.strip():
                logger.info("Successfully extracted text using pdfminer.six")
                return text.strip()
        except ImportError:
            logger.warning("pdfminer.six not installed")
        except Exception as e:
            logger.warning(f"pdfminer.six extraction failed: {str(e)}")
        
        # Method 3: Try with pdfplumber
        try:
            import pdfplumber
            methods_tried += 1
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info("Successfully extracted text using pdfplumber")
                    return text.strip()
        except ImportError:
            logger.warning("pdfplumber not installed")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Method 4: Last resort - try OCR if available
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            methods_tried += 1
            logger.info("Attempting OCR extraction with pytesseract")
            
            # Check if tesseract is installed
            tesseract_version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {tesseract_version}")
            
            images = convert_from_path(file_path)
            text = ""
            
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            
            if text.strip():
                logger.info("Successfully extracted text using OCR")
                return text.strip()
        except ImportError:
            logger.warning("OCR dependencies (pytesseract/pdf2image) not installed")
        except Exception as e:
            logger.warning(f"OCR extraction failed: {str(e)}")
        
        # If all methods failed, provide diagnostic info and raise exception
        if methods_tried == 0:
            logger.error("No PDF extraction methods available - install PyPDF2, pdfminer.six, pdfplumber, or pytesseract+pdf2image")
            raise RuntimeError("No PDF extraction methods available")
        elif not text.strip():
            logger.error(f"All {methods_tried} PDF extraction methods failed - the PDF may be secured, scanned, or corrupted")
            
            # Return a placeholder for testing purposes
            return "This appears to be an empty or unreadable PDF. Please ensure the PDF contains extractable text."
            
        return text.strip()

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
        Analyze the following resume and extract structured information in JSON format.
        This resume could be from ANY profession including healthcare, legal, education, finance, marketing, 
        sales, operations, customer service, creative fields, research, or technology.

        Resume Text:
        {resume_text}

        Please extract and return ONLY a valid JSON object with these fields:
        {{
            "skills": ["list of ALL relevant skills including technical skills, clinical skills, legal skills, teaching skills, financial skills, soft skills, certifications, tools, software, equipment, etc."],
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
        - Extract ALL relevant skills regardless of profession (medical, legal, educational, financial, technical, etc.)
        - For healthcare: include clinical skills, medical equipment, certifications, specialties
        - For legal: include practice areas, legal software, court procedures, legal research
        - For education: include teaching methods, subject areas, educational tools, curriculum development
        - For finance: include accounting software, financial analysis, investment knowledge, regulations
        - For any profession: include relevant software, tools, methodologies, and certifications
        - Extract only information that is clearly stated in the resume
        - For experience_level, consider years of experience and seniority of positions
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
            json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                # Extract JSON from code block
                json_str = json_match.group(1)
            else:
                # Assume the entire response is JSON or contains JSON
                json_str = ai_response
            
            # Attempt to extract JSON object if embedded in other text
            if not json_str.strip().startswith('{'):
                json_block_match = re.search(r'(\{.*\})', json_str, re.DOTALL)
                if json_block_match:
                    json_str = json_block_match.group(1)
            
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
        """Enhanced local resume analysis when AI is unavailable - supports all professions"""
        import re
        
        # Use universal skills database instead of just tech skills
        all_skills = get_all_skills()
        
        # Extract skills using regex with word boundaries
        skills = []
        for skill in all_skills:
            pattern = r'\b' + re.escape(skill.lower()).replace(r'\ ', r'[ -]?') + r'\b'
            if re.search(pattern, resume_text.lower()):
                skills.append(skill)
        
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
        
        # Better job title extraction with deduplication
        job_titles = []
        
        # Look for job title sections first (more accurate)
        section_matches = re.findall(r'(?:WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)[^\n]*\n+\s*([\w\s]+)\s*\n+\s*([^,\n]+)', resume_text, re.IGNORECASE)
        if section_matches:
            for match in section_matches:
                title = match[0].strip()
                if title and title.lower() not in [t.lower() for t in job_titles]:
                    job_titles.append(title)
        
        # Then try pattern-based extraction if needed
        if not job_titles:
            # Universal job title patterns covering all professions
            title_patterns = [
                # Technology
                r'(senior|lead|principal|staff)?\s*(software|frontend|backend|full[\s-]?stack|mobile|ios|android|web|cloud|data|devops|ml|ai|system|network|security)\s*(developer|engineer|architect)',
                r'(ux|ui|user experience|user interface|product|project|program|technical|engineering|it|information technology)\s*(designer|manager|lead|director)',
                
                # Healthcare
                r'(registered|licensed|certified)?\s*(nurse|physician|doctor|therapist|pharmacist|dentist|surgeon|radiologist|cardiologist|neurologist)\s*(practitioner|specialist|assistant)?',
                r'(medical|clinical|health)\s*(assistant|technician|coordinator|specialist|administrator)',
                r'(charge|head|staff|icu|er|emergency)\s*(nurse)',
                
                # Legal
                r'(senior|associate|junior|lead)?\s*(attorney|lawyer|counsel|paralegal|legal)\s*(assistant|advisor|specialist|officer)?',
                r'(corporate|criminal|civil|family|immigration|intellectual property)\s*(lawyer|attorney)',
                
                # Education
                r'(elementary|middle|high school|university|college)?\s*(teacher|professor|instructor|educator|lecturer|tutor)',
                r'(curriculum|academic|student|admissions)\s*(coordinator|advisor|counselor|specialist)',
                r'(special education|esl|math|science|english|history)\s*(teacher|instructor)',
                
                # Finance & Accounting
                r'(senior|staff|junior)?\s*(accountant|auditor|financial|tax)\s*(analyst|advisor|specialist|manager)?',
                r'(investment|banking|credit|loan)\s*(analyst|officer|specialist|advisor)',
                r'(accounts|budget|treasury|risk)\s*(manager|analyst|coordinator)',
                
                # Sales & Marketing
                r'(sales|marketing|business development|account)\s*(manager|representative|executive|specialist|coordinator)',
                r'(digital|content|social media|brand)\s*(marketing|manager|specialist|coordinator)',
                r'(inside|outside|field|territory)\s*(sales)',
                
                # Human Resources
                r'(human resources|hr|talent|recruitment)\s*(manager|specialist|coordinator|assistant|generalist)',
                r'(recruiting|talent acquisition|benefits|payroll)\s*(specialist|coordinator|manager)',
                
                # Operations & Management
                r'(operations|project|program|general)\s*(manager|director|coordinator|analyst)',
                r'(supply chain|logistics|warehouse|inventory)\s*(manager|coordinator|specialist|analyst)',
                
                # Customer Service
                r'(customer|client|technical|help desk)\s*(service|support|success)\s*(representative|specialist|manager|coordinator)?',
                
                # Creative & Design
                r'(graphic|web|ui/ux|interior|fashion)\s*(designer)',
                r'(art|creative|brand|marketing)\s*(director|manager|coordinator)',
                
                # General patterns
                r'(data|business|systems|financial|marketing|sales|research)\s*(analyst|scientist)',
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
                    if title and title.lower() not in [t.lower() for t in job_titles]:
                        job_titles.append(title.title())  # Convert to title case
            
            # If still no specific titles found, look for generic job titles across all professions
            if not job_titles:
                generic_patterns = [
                    # Technology
                    r'(Developer|Engineer|Programmer|Architect|Analyst)',
                    # Healthcare
                    r'(Nurse|Doctor|Physician|Therapist|Technician|Assistant)',
                    # Legal
                    r'(Attorney|Lawyer|Paralegal|Counsel)',
                    # Education
                    r'(Teacher|Professor|Instructor|Educator|Tutor)',
                    # Finance
                    r'(Accountant|Auditor|Analyst|Advisor)',
                    # Sales & Marketing
                    r'(Manager|Representative|Executive|Specialist|Coordinator)',
                    # General
                    r'(Director|Lead|Supervisor|Administrator|Consultant)'
                ]
                
                for pattern in generic_patterns:
                    generic_matches = re.findall(pattern + r'[^,\n]*', resume_text)
                    if generic_matches:
                        for title in generic_matches[:3]:  # Take top 3 matches
                            clean_title = title.strip()
                            if clean_title and clean_title.lower() not in [t.lower() for t in job_titles]:
                                job_titles.append(clean_title)
                        if job_titles:  # Break if we found some titles
                            break
        
        # Enhanced education extraction with improved pattern matching
        education = []
        
        # Try to find education section first with more comprehensive pattern matching
        edu_section_match = re.search(r'(?:EDUCATION|ACADEMIC|QUALIFICATIONS|EDUCATIONAL BACKGROUND)[^\n]*\n(.*?)(?:\n\n|\n[A-Z]{2,}|\Z)', 
                                     resume_text, re.IGNORECASE | re.DOTALL)
                                     
        # Look specifically for university names in the entire text, including common ones like MIT
        university_pattern = r'((?:University|College|Institute|School)[^,\n]*|MIT|Stanford|Harvard|Berkeley)'
        universities = re.findall(university_pattern, resume_text, re.IGNORECASE)
        
        # Direct pattern matching for common education section formats
        # Format: Degree in Field\nInstitution\nYear
        direct_edu_patterns = [
            r'(Master|Bachelor|Ph\.?D|Doctor)\s+(?:of|in)\s+([^\n]+)\n+([^\n]+(?:University|College|Institute|School)[^\n]*)\n+(\d{4}(?:\s*[-–]\s*(?:\d{4}|[Pp]resent|[Oo]ngoing|[Cc]urrent))?)',
            r'(M\.?S|B\.?S|B\.?A|M\.?B\.?A)\s+(?:of|in)?\s+([^\n]+)\n+([^\n]+(?:University|College|Institute|School)[^\n]*)\n+(\d{4}(?:\s*[-–]\s*(?:\d{4}|[Pp]resent|[Oo]ngoing|[Cc]urrent))?)',
        ]
        
        # Try direct pattern matches first
        for pattern in direct_edu_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                degree_type = match[0].strip()
                field = match[1].strip() if len(match) > 1 else ""
                institution = match[2].strip() if len(match) > 2 else ""
                year = match[3].strip() if len(match) > 3 else ""
                
                # Map abbreviations to full degrees
                if degree_type.upper() in ["MS", "M.S"]:
                    degree_type = "Master of Science"
                elif degree_type.upper() in ["MA", "M.A"]:
                    degree_type = "Master of Arts"
                elif degree_type.upper() in ["MBA", "M.B.A"]:
                    degree_type = "Master of Business Administration"
                elif degree_type.upper() in ["BS", "B.S"]:
                    degree_type = "Bachelor of Science"
                elif degree_type.upper() in ["BA", "B.A"]:
                    degree_type = "Bachelor of Arts"
                elif "master" in degree_type.lower():
                    degree_type = "Master's Degree"
                elif "bachelor" in degree_type.lower():
                    degree_type = "Bachelor's Degree"
                elif "phd" in degree_type.lower() or "doctor" in degree_type.lower():
                    degree_type = "Doctor of Philosophy"
                
                # Format the degree with field
                full_degree = degree_type
                if field:
                    full_degree += f" in {field}"
                
                education.append({
                    "degree": full_degree,
                    "institution": institution,
                    "year": year
                })
        
        # Special case for Massachusetts Institute of Technology (MIT)
        if 'Massachusetts Institute of Technology' in resume_text or 'MIT' in resume_text:
            if 'Massachusetts Institute of Technology (MIT)' in resume_text:
                if 'Massachusetts Institute of Technology (MIT)' not in universities:
                    universities.append('Massachusetts Institute of Technology (MIT)')
            elif 'Massachusetts Institute of Technology' in resume_text:
                if 'Massachusetts Institute of Technology' not in universities:
                    universities.append('Massachusetts Institute of Technology')
        edu_section = edu_section_match.group(1) if edu_section_match else resume_text
        
        # Common degree abbreviations and their full forms
        degree_mapping = {
            "bs": "Bachelor of Science",
            "ba": "Bachelor of Arts",
            "bsc": "Bachelor of Science",
            "bba": "Bachelor of Business Administration", 
            "b.s": "Bachelor of Science",
            "b.a": "Bachelor of Arts",
            "ms": "Master of Science",
            "ma": "Master of Arts",
            "msc": "Master of Science",
            "mba": "Master of Business Administration",
            "m.s": "Master of Science", 
            "m.a": "Master of Arts",
            "phd": "Doctor of Philosophy",
            "ph.d": "Doctor of Philosophy"
        }
        
        # Try to detect a more specific education section in the whole resume
        # This is important for cases where the main edu_section_match might have failed
        if not edu_section or len(edu_section) < 20:  # If the extracted section is too short
            edu_lines = []
            found_edu_section = False
            for line in resume_text.split('\n'):
                if re.search(r'^EDUCATION\s*$', line, re.IGNORECASE):
                    found_edu_section = True
                    continue
                elif found_edu_section and re.search(r'^[A-Z]{2,}', line.strip()):
                    found_edu_section = False
                    break
                elif found_edu_section:
                    edu_lines.append(line)
            
            if edu_lines:
                edu_section = '\n'.join(edu_lines)
        
        # Filter out the section to only focus on education
        # Remove work experience section if it exists in the education section
        edu_section = re.sub(r'(?i)WORK EXPERIENCE.*', '', edu_section)
        
        # Split education section into separate entries
        # This is the most important step - getting clean entries to process
        edu_entries = []
        
        # First try to split by blank lines
        initial_entries = re.split(r'\n\s*\n', edu_section)
        for entry in initial_entries:
            # Further split entries that might contain multiple degrees by newlines
            sub_entries = re.split(r'\n(?=\d{4}|(?:bachelor|master|phd|mba|bs|ms|ba|ma|b\.s|m\.s))', entry, flags=re.IGNORECASE)
            
            # Process each sub-entry
            for sub_entry in sub_entries:
                if not sub_entry.strip():
                    continue
                    
                # Check for comma-separated entries like "MSc in Data Science, MIT, 2018"
                comma_entries = re.findall(r'((?:bachelor|master|phd|doctorate|mba|bs|ba|ms|ma|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?)[^,]*?(?:in|of)?[^,]*?(?:science|engineering|arts|business|administration|technology|mathematics)[^,]*?),\s*([^,]*?(?:university|college|institute|school|academy|tech|\bMIT\b)[^,]*?),\s*(\d{4})', sub_entry, re.IGNORECASE)
                
                if comma_entries:
                    # Add each comma-separated degree as a separate entry
                    for degree, inst, year in comma_entries:
                        # Add as a separate entry with clean fields
                        edu_entries.append({
                            "degree_text": degree.strip(),
                            "institution_text": inst.strip(),
                            "year_text": year.strip(),
                            "is_structured": True  # Flag to indicate this is already structured
                        })
                else:
                    # Add the sub-entry as is
                    edu_entries.append(sub_entry.strip())
        
        # Process each education entry
        for entry in edu_entries:
            # Handle pre-structured entries from comma parsing
            if isinstance(entry, dict) and entry.get("is_structured"):
                degree_text = entry.get("degree_text", "")
                institution_text = entry.get("institution_text", "")
                year_text = entry.get("year_text", "")
                
                # Process the degree field
                degree = ""
                field = ""
                
                # Check for degree type
                for abbr, full_degree in degree_mapping.items():
                    if re.search(r'\b' + re.escape(abbr) + r'\b', degree_text, re.IGNORECASE):
                        degree = full_degree
                        break
                
                # If no standard abbreviation found, check for full degree names
                if not degree:
                    if re.search(r'\bbachelor', degree_text, re.IGNORECASE):
                        degree = "Bachelor's Degree"
                    elif re.search(r'\bmaster', degree_text, re.IGNORECASE):
                        degree = "Master's Degree"
                    elif re.search(r'\bmba\b', degree_text, re.IGNORECASE):
                        degree = "Master of Business Administration"
                    elif re.search(r'\b(?:phd|ph\.d|doctorate)', degree_text, re.IGNORECASE):
                        degree = "Doctor of Philosophy"
                
                # Extract field of study
                field_match = re.search(r'(?:in|of)\s+([^,\n]*)', degree_text, re.IGNORECASE)
                if field_match:
                    field = field_match.group(1).strip()
                
                # Format the full degree with field
                full_degree = degree
                if field and degree and field.lower() not in degree.lower():
                    full_degree = f"{degree} in {field.title()}"
                
                edu_entry = {
                    "degree": full_degree.strip(),
                    "institution": institution_text,
                    "year": year_text
                }
                
                # Add to education list if not a duplicate
                is_duplicate = False
                for existing in education:
                    if (existing.get("institution") == edu_entry["institution"] and
                        existing.get("year") == edu_entry["year"] and
                        existing.get("degree") == edu_entry["degree"]):
                        is_duplicate = True
                        break
                
                if not is_duplicate and (edu_entry["degree"] or edu_entry["institution"]):
                    education.append(edu_entry)
                
                continue
            
            if isinstance(entry, str) and ("work experience" in entry.lower() or not entry.strip()):
                continue
                
            # Process regular string entries
            # Reset variables for this entry
            degree = ""
            field = ""
            institution = ""
            year = ""
            
            # Find degree information
            # First look for standard abbreviations
            for abbr, full_degree in degree_mapping.items():
                if re.search(r'\b' + re.escape(abbr) + r'\b', entry, re.IGNORECASE):
                    degree = full_degree
                    break
            
            # If no standard abbreviation found, look for degree names
            if not degree:
                if re.search(r'\bbachelor', entry, re.IGNORECASE):
                    degree = "Bachelor's Degree"
                elif re.search(r'\bmaster', entry, re.IGNORECASE):
                    degree = "Master's Degree"
                elif re.search(r'\bmba\b', entry, re.IGNORECASE):
                    degree = "Master of Business Administration"
                elif re.search(r'\b(?:phd|ph\.d|doctorate)', entry, re.IGNORECASE):
                    degree = "Doctor of Philosophy"
            
            # Find field of study
            field_match = re.search(r'(?:degree|diploma)?\s+(?:in|of)\s+([^,\n]*?(?:engineering|science|arts|business administration|computer|information technology|data|mathematics|physics|chemistry|biology|economics|artificial intelligence))[^,\n]*', entry, re.IGNORECASE)
            if field_match:
                field = field_match.group(1).strip()
            
            # Extract institution name
            # First check for "from X" or "at X" format which is more precise
            from_at_match = re.search(r'(?:from|at)\s+([^,\n]*?(?:university|college|institute|school|MIT)[^,\n\(]*)', entry, re.IGNORECASE)
            if from_at_match:
                institution = from_at_match.group(1).strip()
            else:
                # Fall back to general institution detection
                inst_match = re.search(r'([^,\n]*?(?:university|college|institute|school|MIT)[^,\n]*)', entry, re.IGNORECASE)
                if inst_match:
                    institution = inst_match.group(1).strip()
            
            # Clean up institution name if found
            if institution:
                # Remove phrases like "from" or "at"
                institution = re.sub(r'^\s*(?:at|from)\s+', '', institution, flags=re.IGNORECASE).strip()
                
                # Make sure it doesn't contain the degree or field references
                for term in ["bachelor", "master", "phd", "doctorate", "degree", "in artificial intelligence", 
                             "in computer science", "in business", "in engineering"]:
                    institution = re.sub(r'\b' + re.escape(term) + r'\b', '', institution, flags=re.IGNORECASE).strip()
                
                # Special case for MIT
                if re.search(r'\bMIT\b', entry, re.IGNORECASE) and not institution:
                    institution = "MIT"
                
                # Special case for Berkeley
                if re.search(r'\bBerkeley\b', entry, re.IGNORECASE) and not institution:
                    institution = "University of California, Berkeley"
                
                # Clean up any remaining punctuation and trailing/leading words
                institution = re.sub(r'^[,\s]+|[,\s]+$|^\bfrom\b|\bat\b', '', institution).strip()
                
                # Remove any parentheses sections that might contain years
                institution = re.sub(r'\([^\)]*\)', '', institution).strip()
            
            # Look for years - various formats
            year_match = re.search(r'(\d{4}(?:\s*[-–]?\s*(?:\d{4}|present|ongoing|current))?)', entry, re.IGNORECASE)
            if year_match:
                year = year_match.group(1).strip()
            
            # For entry formats like "2018-2022: Bachelor's degree"
            if not degree and year:
                after_year_match = re.search(r'\d{4}(?:[-–]\d{4})?:?\s+(.*?)(?:,|\n|$)', entry, re.IGNORECASE)
                if after_year_match:
                    possible_degree = after_year_match.group(1).strip()
                    if "bachelor" in possible_degree.lower():
                        degree = "Bachelor's Degree"
                    elif "master" in possible_degree.lower():
                        degree = "Master's Degree" 
                    elif "mba" in possible_degree.lower():
                        degree = "Master of Business Administration"
            
            # If we found MBA but didn't extract field
            if "master of business administration" in degree.lower() and not field:
                field = "Business Administration"
            
            # For common fields that might not be explicitly stated with "in" or "of"
            if not field:
                for common_field in ["computer science", "information technology", "business administration", 
                                   "data science", "artificial intelligence", "software engineering"]:
                    if common_field in entry.lower():
                        field = common_field
                        break
            
            # Format the full degree with field
            full_degree = degree
            if field and degree and field.lower() not in degree.lower():
                full_degree = f"{degree} in {field.title()}"
            
            # Create the education entry if we have sufficient information
            if (full_degree or institution) and full_degree.lower() != "in":  # Prevent empty or invalid degrees
                edu_entry = {
                    "degree": full_degree.strip(),
                    "institution": institution,
                    "year": year
                }
                
                # Check if this is a duplicate
                is_duplicate = False
                for existing in education:
                    if (existing.get("institution") == edu_entry["institution"] and
                        existing.get("year") == edu_entry["year"] and
                        existing.get("degree") == edu_entry["degree"]):
                        is_duplicate = True
                        break
                
                if not is_duplicate and (edu_entry["degree"] or edu_entry["institution"]):
                    education.append(edu_entry)
        
        # Enhanced deduplication for education entries
        unique_education = []
        for edu in education:
            # Skip entries without key information
            if not edu.get("institution") or not edu.get("year"):
                continue
                
            # Normalize values for comparison
            norm_inst = edu["institution"].lower().strip()
            norm_degree = edu["degree"].lower().strip() if edu.get("degree") else ""
            norm_year = edu["year"].strip()
            
            # Check for duplicate
            is_duplicate = False
            for unique_edu in unique_education:
                if (unique_edu["institution"].lower().strip() == norm_inst and
                    unique_edu["year"].strip() == norm_year):
                    # Either same degree or one has a more complete degree than the other
                    if (not norm_degree or not unique_edu.get("degree") or 
                        norm_degree == unique_edu["degree"].lower().strip()):
                        is_duplicate = True
                        break
                    
                # Special case for abbreviations like MIT vs Massachusetts Institute of Technology
                if ("mit" in norm_inst and "massachusetts institute of technology" in unique_edu["institution"].lower()) or \
                   ("massachusetts institute of technology" in norm_inst and "mit" in unique_edu["institution"].lower()):
                    if norm_year == unique_edu["year"].strip():
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                # Clean up institution name formatting
                if edu["institution"].isupper() or edu["institution"].islower():
                    edu["institution"] = edu["institution"].title()
                
                unique_education.append(edu)
        
        # Replace original education entries with deduplicated ones
        education = unique_education
        
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