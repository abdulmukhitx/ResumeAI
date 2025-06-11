#!/usr/bin/env python
"""
Test script for HH.ru API integration in Smart Resume Matcher
This script tests the location resolution functionality and job search
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from jobs.services import HHApiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_location_resolution():
    """Test the location resolution functionality"""
    client = HHApiClient()
    
    test_locations = [
        "Almaty",
        "ASTANA",  # Test case insensitivity
        "Moscow",
        "Almaty, Kazakhstan",  # Test comma separation
        "160",  # Test numeric ID
        None,   # Test None value
        "Unknown City"  # Test fallback
    ]
    
    print("\n===== TESTING LOCATION RESOLUTION =====")
    for location in test_locations:
        resolved = client._resolve_location(location)
        print(f"Location: {location} -> Resolved to: {resolved}")

def test_job_search():
    """Test the job search functionality"""
    client = HHApiClient()
    
    test_searches = [
        {"text": "Python Developer", "area": "Almaty"},
        {"text": "Frontend Developer", "area": "Moscow"},
        {"text": "Data Scientist", "area": "Astana"}
    ]
    
    print("\n===== TESTING JOB SEARCH =====")
    for search in test_searches:
        try:
            print(f"\nSearching for '{search['text']}' in {search['area']}...")
            results = client.search_vacancies(search)
            found = results.get('found', 0)
            items = results.get('items', [])
            print(f"Found {found} jobs, displaying first {min(3, len(items))} results:")
            
            for i, item in enumerate(items[:3]):
                print(f"{i+1}. {item.get('name')} at {item.get('employer', {}).get('name')}")
                print(f"   Location: {item.get('area', {}).get('name')}")
                if item.get('salary'):
                    salary_from = item['salary'].get('from', 'N/A')
                    salary_to = item['salary'].get('to', 'N/A')
                    currency = item['salary'].get('currency', '')
                    print(f"   Salary: {salary_from} - {salary_to} {currency}")
                else:
                    print("   Salary: Not specified")
                print(f"   URL: {item.get('alternate_url')}")
                print()
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")

if __name__ == '__main__':
    test_location_resolution()
    test_job_search()
