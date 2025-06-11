web: cd smart_resume_matcher && gunicorn --log-file=- config.wsgi:application --bind 0.0.0.0:$PORT
worker: cd smart_resume_matcher && celery -A config worker --loglevel=info
beat: cd smart_resume_matcher && celery -A config beat --loglevel=info
