# Smart Resume Matcher

An AI-powered resume analysis and job matching platform that helps you find the perfect job match based on your skills and experience.

## Features

- **Resume Analysis**: Upload your resume and get intelligent analysis of your skills, experience, and qualifications
- **AI-Powered Job Matching**: Our advanced algorithm analyzes your resume and finds the best job opportunities that match your unique profile
- **Skills-Based Matching**: See how your skills align with job requirements and identify skill gaps
- **Job Search**: Search for jobs using custom filters and see your match score for each position
- **Application Tracking**: Keep track of your job applications and their status

## Getting Started

### For Users

1. Create an account
2. Upload your resume (PDF format)
3. Use the "AI Job Matches" feature to find the best opportunities
4. Apply to positions that interest you
5. Track your applications

The system will automatically analyze your resume and match you with suitable job positions.

### For Developers

#### Prerequisites

- Python 3.8+
- SQLite (included) or PostgreSQL

#### Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Deployment on Render

### Manual Deployment
1. Sign up for a Render account: [https://render.com/](https://render.com/)
2. Connect your GitHub repository
3. Create a new Web Service and select your repository
4. Configure the following settings:
   - **Name**: smart-resume-matcher
   - **Environment**: Python
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. Add the required environment variables:
   - `SECRET_KEY`: A long, random string
   - `DEBUG`: false
   - `ALLOWED_HOSTS`: your-app.render.com
   - `DATABASE_URL`: Your PostgreSQL connection string (create a PostgreSQL database in Render first)
   - `REDIS_URL`: Your Redis connection string (create a Redis instance in Render first)
6. Create the worker process for Celery using the same repo but with start command: `celery -A config worker --loglevel=info`
7. Create the beat process for Celery using the same repo but with start command: `celery -A config beat --loglevel=info`
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create admin user:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the application.

## External Services

The application can connect to these external services if configured:

- **HH.ru API**: For job search functionality
- **AI Analysis**: Enhanced resume analysis (optional)

## Development

### Running Tests

```bash
python manage.py test
```

### Running with Docker

```bash
docker-compose up -d
```

## License

This project is licensed under the MIT License.
