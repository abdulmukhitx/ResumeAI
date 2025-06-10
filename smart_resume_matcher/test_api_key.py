# Test script for AI analyzer with improved debugging
import os
import re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import requests
import json

def test_api_key():
    print("Testing GROQ API Key...")
    
    # Check if API key exists and its format
    api_key = settings.GROQ_API_KEY
    masked_key = api_key[:6] + '*******' if api_key else 'None'
    print(f"API Key: {masked_key}")
    
    # Check if the format looks like a real Groq API key (should start with 'gsk_')
    if not api_key.startswith('gsk_'):
        print("WARNING: API key doesn't start with 'gsk_'. This doesn't appear to be a valid Groq API key.")
    
    # Try a simple API call to validate
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    data = {
        'model': 'llama3-8b-8192',
        'messages': [
            {
                'role': 'system',
                'content': 'You are a helpful assistant.'
            },
            {
                'role': 'user',
                'content': 'Say hello!'
            }
        ],
        'temperature': 0.3,
        'max_tokens': 100,
    }
    
    try:
        print("Making test API call...")
        response = requests.post('https://api.groq.com/openai/v1/chat/completions', 
                                headers=headers, 
                                json=data,
                                timeout=15)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! API key is valid.")
            result = response.json()
            message = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"Response: {message[:100]}...")
        else:
            print(f"Error response: {response.text[:500]}")
            
    except Exception as e:
        print(f"API call failed: {str(e)}")

if __name__ == "__main__":
    test_api_key()
