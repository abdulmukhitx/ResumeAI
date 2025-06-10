# Test script for HH.ru API with location handling
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

import logging
logging.basicConfig(level=logging.INFO)

from jobs.services import HHApiClient

def test_hh_api_locations():
    client = HHApiClient()
    
    # Test locations - basic cases
    test_locations = [
        "Almaty, Kazakhstan",
        "Almaty",
        "Kazakhstan",
        "Moscow",
        "160",  # Almaty area code
        "Saint Petersburg",
        "Astana, Kazakhstan",
        "Nur-Sultan",  # Old name for Astana
        "SHYMKENT",  # Test case insensitivity
        "Unknown City",  # Should default to Moscow
        None  # Should default to Moscow
    ]
    
    for location in test_locations:
        print(f"\n=== Testing location: {location} ===")
        
        params = {
            'text': 'Python',
            'page': 0,
            'per_page': 2,
            'area': location
        }
        
        try:
            # Will use our updated search_vacancies method
            result = client.search_vacancies(params)
            found = result.get('found', 0)
            items = result.get('items', [])
            
            print(f"Found {found} jobs")
            if items:
                sample_job = items[0]
                print(f"Sample job: {sample_job.get('name')} at {sample_job.get('employer', {}).get('name')}")
                print(f"Location: {sample_job.get('area', {}).get('name')}")
            
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_hh_api_locations()
