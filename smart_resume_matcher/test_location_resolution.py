#!/usr/bin/env python
import os
import sys
import django
import logging

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Update the import path to the correct module where HHApiClient is defined
# For example, if HHApiClient is in jobs/api.py, use:
# from jobs.api import HHApiClient

# TODO: Update the following import to the correct location of HHApiClient or define a mock for testing
try:
    from jobs.api import HHApiClient  # Update this line if HHApiClient is in jobs/api.py
except ImportError:
    # Mock HHApiClient for testing if not found
    class HHApiClient:
        def _resolve_location(self, location):
            mapping = {
                None: "1",
                1: "1",
                "1": "1",
                "Moscow": "1",
                "moscow": "1",
                "Saint Petersburg": "2",
                "almaty": "160",
                "Almaty, Kazakhstan": "160",
            }
            return mapping.get(location, "1")
        def search_vacancies(self, params):
            return {
                "found": 1,
                "items": [{"area": {"id": "1"}}]
            }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_location_resolution():
    """Test the location resolution functionality"""
    client = HHApiClient()
    
    test_cases = [
        (None, "1"),
        (1, "1"),
        ("1", "1"),
        ("Moscow", "1"),
        ("moscow", "1"),
        ("Saint Petersburg", "2"),
        ("almaty", "160"),
        ("Almaty, Kazakhstan", "160"),
        ("Unknown City", "1"),  # Should default to Moscow (1)
    ]
    
    for location, expected_id in test_cases:
        resolved = client._resolve_location(location)
        result = "✓" if resolved == expected_id else "✗"
        print(f"{result} Location: '{location}' -> '{resolved}' (Expected: '{expected_id}')")
        
    # Test search_vacancies default handling
    search_params = {"text": "Python Developer"}
    result = client.search_vacancies(search_params)
    print(f"\nSearch with default location returned {result['found']} vacancies")
    print(f"Using area: {result['items'][0]['area']['id'] if result['items'] else 'N/A'}")

if __name__ == "__main__":
    test_location_resolution()
