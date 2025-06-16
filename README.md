

Smart Resume Matcher
An AI-powered resume analysis and job matching platform that helps you find the perfect job match based on your skills and experience.

Features
Resume Analysis: Upload your resume and get intelligent analysis of your skills, experience, and qualifications
AI-Powered Job Matching: Our advanced algorithm analyzes your resume and finds the best job opportunities that match your unique profile
Skills-Based Matching: See how your skills align with job requirements and identify skill gaps
Job Search: Search for jobs using custom filters and see your match score for each position
Application Tracking: Keep track of your job applications and their status
Getting Started
For Users
Create an account
Upload your resume (PDF format)
Use the "AI Job Matches" feature to find the best opportunities
Apply to positions that interest you
Track your applications
The system will automatically analyze your resume and match you with suitable job positions.

For Developers
Prerequisites
Python 3.8+
SQLite (included) or PostgreSQL
Installation
Clone the repository
Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt
Deployment on Render
Manual Deployment
Sign up for a Render account: https://render.com/
Connect your GitHub repository
Create a new Web Service and select your repository
Configure the following settings:
Name: smart-resume-matcher
Environment: Python
Build Command: ./build.sh
Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
Add the required environment variables:
SECRET_KEY: A long, random string
DEBUG: false
ALLOWED_HOSTS: your-app.render.com
DATABASE_URL: Your PostgreSQL connection string (create a PostgreSQL database in Render first)
REDIS_URL: Your Redis connection string (create a Redis instance in Render first)
Create the worker process for Celery using the same repo but with start command: celery -A config worker --loglevel=info
Create the beat process for Celery using the same repo but with start command: celery -A config beat --loglevel=info pip install -r requirements.txt

4. Run migrations:
```bash
python manage.py migrate
Create admin user:
python manage.py createsuperuser
Run the development server:
python manage.py runserver
Visit http://127.0.0.1:8000/ to access the application.

External Services
The application can connect to these external services if configured:

HH.ru API: For job search functionality
AI Analysis: Enhanced resume analysis (optional)
Development
Running Tests
python manage.py test
Running with Docker
docker-compose up -d
License
This project is licensed under the MIT License.
