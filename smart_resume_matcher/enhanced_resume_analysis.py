"""
Enhanced resume analysis with better error handling and logging for production
"""

def analyze_resume(resume_id):
    """
    Analyze the resume using AI with enhanced error handling for production.
    """
    import logging
    from django.db import transaction
    from django.conf import settings
    
    # Configure logger
    logger = logging.getLogger(__name__)
    
    # Add console handler for production debugging
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
    
    logger.info(f"Starting resume analysis for ID: {resume_id}")
    
    try:
        # Get resume with retry logic
        max_retries = 3
        resume = None
        
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    resume = Resume.objects.select_for_update().get(id=resume_id)
                    break
            except Resume.DoesNotExist:
                logger.error(f"Resume with ID {resume_id} not found")
                return False
            except Exception as e:
                logger.warning(f"Database lock on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                import time
                time.sleep(1)  # Wait 1 second before retry
        
        if not resume:
            logger.error(f"Could not acquire resume after {max_retries} attempts")
            return False
        
        logger.info(f"Processing resume: {resume.original_filename} for user: {resume.user.email}")
        
        # Update status
        resume.status = 'processing'
        resume.analysis_started_at = timezone.now()
        resume.save(update_fields=['status', 'analysis_started_at'])
        
        # Initialize AI analyzer with error handling
        try:
            analyzer = AIAnalyzer()
            logger.info("AI Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Analyzer: {e}")
            resume.status = 'failed'
            resume.save(update_fields=['status'])
            return False
        
        # Extract text from PDF with enhanced error handling
        try:
            if not resume.file:
                raise ValueError("No file attached to resume")
            
            if not os.path.exists(resume.file.path):
                raise FileNotFoundError(f"Resume file not found: {resume.file.path}")
            
            logger.info(f"Extracting text from: {resume.file.path}")
            resume.raw_text = analyzer.extract_text_from_pdf(resume.file.path)
            
            if not resume.raw_text or len(resume.raw_text.strip()) < 10:
                logger.warning("Very little text extracted from PDF")
                resume.raw_text = "Error: Minimal text extracted from resume."
            else:
                logger.info(f"Successfully extracted {len(resume.raw_text)} characters")
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            resume.raw_text = f"Error extracting text from resume: {str(e)}"
        
        # Save the raw text
        resume.save(update_fields=['raw_text'])
        
        # Analyze the resume with enhanced error handling
        try:
            logger.info("Starting AI analysis...")
            analysis_results = analyzer.analyze_resume(resume.raw_text)
            logger.info(f"AI analysis completed. Results: {analysis_results}")
            
            if not analysis_results or not isinstance(analysis_results, dict):
                logger.error("AI analysis returned invalid results")
                analysis_results = {
                    'skills': [],
                    'experience_level': 'junior',
                    'job_titles': [],
                    'education': [],
                    'work_experience': [],
                    'summary': 'Analysis failed - using fallback analysis',
                    'confidence_score': 0.0
                }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback analysis
            analysis_results = {
                'skills': extract_fallback_skills(resume.raw_text),
                'experience_level': 'junior',
                'job_titles': [],
                'education': [],
                'work_experience': [],
                'summary': f'Fallback analysis used due to AI error: {str(e)}',
                'confidence_score': 0.3
            }
        
        # Update resume with analysis results
        try:
            with transaction.atomic():
                resume.refresh_from_db()
                
                # Ensure we have valid data
                resume.extracted_skills = analysis_results.get('skills', [])
                resume.experience_level = analysis_results.get('experience_level', 'junior')
                resume.job_titles = analysis_results.get('job_titles', [])
                resume.education = analysis_results.get('education', [])
                resume.work_experience = analysis_results.get('work_experience', [])
                resume.analysis_summary = analysis_results.get('summary', 'Resume analyzed successfully')
                resume.confidence_score = analysis_results.get('confidence_score', 0.5)
                
                # Update status
                resume.status = 'completed'
                resume.analysis_completed_at = timezone.now()
                resume.save()
                
                logger.info(f"Resume analysis completed successfully:")
                logger.info(f"  Skills: {len(resume.extracted_skills)} extracted")
                logger.info(f"  Experience: {resume.experience_level}")
                logger.info(f"  Status: {resume.status}")
                
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            resume.status = 'failed'
            resume.save(update_fields=['status'])
            return False
        
        # Find matching jobs with error handling
        try:
            logger.info("Finding matching jobs...")
            find_matching_jobs(resume)
            logger.info("Job matching completed")
        except Exception as e:
            logger.error(f"Error finding matching jobs: {e}")
            # Don't fail the whole process if job matching fails
        
        logger.info(f"Resume analysis pipeline completed successfully for ID: {resume_id}")
        return True
        
    except Exception as e:
        logger.error(f"Resume analysis failed for ID {resume_id}: {e}")
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.status = 'failed'
            resume.save(update_fields=['status'])
        except:
            pass
        return False

def extract_fallback_skills(text):
    """Fallback skill extraction when AI fails"""
    import re
    
    if not text:
        return []
    
    # Common programming languages and technologies
    tech_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'spring',
        'node', 'express', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
        'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux', 'bash'
    ]
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    found_skills = []
    
    for skill in tech_skills:
        if re.search(r'\b' + skill + r'\b', text_lower):
            found_skills.append(skill.title())
    
    return found_skills[:10]  # Limit to 10 skills
