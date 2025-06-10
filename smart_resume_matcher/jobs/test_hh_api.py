import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from jobs.services import HHApiClient

def test_hh_api():
    client = HHApiClient()
    
    # Test search_vacancies
    try:
        print("Testing search_vacancies...")
        params = {'text': 'developer', 'page': 0, 'per_page': 5}
        vacancies = client.search_vacancies(params)
        print("Vacancies fetched successfully:", vacancies)
    except Exception as e:
        print("Error in search_vacancies:", e)
    
    # Test get_vacancy_details
    try:
        print("Testing get_vacancy_details...")
        vacancy_id = '121344506'  # Replace with a valid ID from the fetched vacancies
        details = client.get_vacancy_details(vacancy_id)
        print("Vacancy details fetched successfully:", details)
    except Exception as e:
        print("Error in get_vacancy_details:", e)

if __name__ == "__main__":
    test_hh_api()