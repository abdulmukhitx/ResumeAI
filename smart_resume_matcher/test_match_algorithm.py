"""
Simplified test for job matching algorithm without database operations
"""

def test_match_algorithm():
    """Test the core job matching algorithm logic"""
    print("\n===== Testing Job Matching Algorithm =====")
    
    # Mock resume data
    resume = {
        'extracted_skills': ['python', 'django', 'flask', 'fastapi', 'rest api', 'git'],
        'experience_level': 'middle', 
        'job_titles': ['Python Developer', 'Backend Engineer']
    }
    
    # Mock job data
    jobs = [
        {
            'id': 'job1',
            'name': 'Senior Python Developer', 
            'description': 'Looking for Python developer with Django and Flask experience',
            'snippet': {
                'requirement': 'Python, Django, Flask, RESTful APIs, Git',
                'responsibility': 'Build and maintain web applications'
            },
            'employer': {
                'name': 'Tech Company'
            }
        },
        {
            'id': 'job2',
            'name': 'Full Stack Developer',
            'description': 'Looking for a full stack developer with JavaScript skills',
            'snippet': {
                'requirement': 'JavaScript, React, TypeScript, Node.js',
                'responsibility': 'Build front-end and back-end services'
            },
            'employer': {
                'name': 'Web Agency'
            }
        },
        {
            'id': 'job3',
            'name': 'Junior Python Developer',
            'description': 'Entry level position for a Python developer',
            'snippet': {
                'requirement': 'Python, Git, SQL',
                'responsibility': 'Assist in web development tasks'
            },
            'employer': {
                'name': 'Startup'
            }
        }
    ]
    
    # Mock job matcher
    class MockJobMatcher:
        def __init__(self, resume_data):
            self.resume = resume_data
            
        def _extract_skills_from_job(self, job_data):
            """Extract skills from job description and requirements"""
            full_text = ' '.join([
                job_data.get('description', ''),
                job_data.get('snippet', {}).get('requirement', ''),
                job_data.get('snippet', {}).get('responsibility', '')
            ]).lower()
            
            tech_skills = [
                "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "ruby", "php", "swift",
                "html", "css", "sql", "nosql", "react", "angular", "vue", "django", "flask", "fastapi",
                "docker", "kubernetes", "aws", "git", "rest", "api", "restful"
            ]
            
            skills = set()
            for skill in tech_skills:
                if skill in full_text:
                    skills.add(skill)
                    
            return skills
            
        def calculate_match_score(self, job_data):
            """Calculate match score between resume and job"""
            # Extract job skills
            job_skills = self._extract_skills_from_job(job_data)
            
            # Get resume skills
            resume_skills = set(self.resume['extracted_skills'])
            
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
            experience_level = self.resume['experience_level'].lower()
            job_title = job_data.get('name', '').lower()
            job_requirements = job_data.get('snippet', {}).get('requirement', '').lower()
            
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
    
    # Create matcher with resume data
    matcher = MockJobMatcher(resume)
    
    # Calculate match score for each job
    job_matches = []
    
    for job in jobs:
        match_score, match_details = matcher.calculate_match_score(job)
        job_matches.append((job, match_score, match_details))
        
        print(f"\nJob: {job['name']}")
        print(f"Match Score: {match_score}")
        print(f"Skill Score: {match_details['skill_score']}")
        print(f"Experience Score: {match_details['experience_score']}")
        print(f"Matching Skills: {', '.join(match_details['matching_skills'])}")
        print(f"Missing Skills: {', '.join(match_details['missing_skills'])}")
    
    # Sort by match score (descending)
    job_matches.sort(key=lambda x: x[1], reverse=True)
    
    print("\nRanked Job Matches:")
    for i, (job, score, _) in enumerate(job_matches, 1):
        print(f"{i}. {job['name']} - {score}% Match")
    
    print("\n===== Test Complete =====")

if __name__ == "__main__":
    test_match_algorithm()
