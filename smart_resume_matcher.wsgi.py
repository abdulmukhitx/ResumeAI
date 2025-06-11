"""
WSGI config for smart_resume_matcher project.

This module contains a simple redirect to the actual WSGI application in the config folder.
"""

import os
import sys

# Add the smart_resume_matcher directory to the path
base_dir = os.path.dirname(os.path.abspath(__file__))
smart_resume_matcher_dir = os.path.join(base_dir, 'smart_resume_matcher')
if smart_resume_matcher_dir not in sys.path:
    sys.path.insert(0, smart_resume_matcher_dir)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import and get the WSGI application from the actual config
from config.wsgi import application  # noqa
