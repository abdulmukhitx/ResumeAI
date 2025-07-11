from django.shortcuts import render
from django.http import JsonResponse
import json

def debug_login_view(request):
    """Debug login view to test the login process"""
    return render(request, 'debug_login.html')
