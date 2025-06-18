"""
JWT-Compatible View Decorator
This decorator replaces @login_required and works with both session and JWT authentication.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)

def jwt_login_required(view_func):
    """
    Decorator that checks for both session and JWT authentication.
    Replaces Django's @login_required for JWT-compatible views.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # Try JWT authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                jwt_auth = JWTAuthentication()
                token = auth_header.split(' ')[1]
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)
                
                if user and user.is_active:
                    # Set user on request
                    request.user = user
                    logger.debug(f"JWT authentication successful for user: {user.email}")
                    return view_func(request, *args, **kwargs)
                    
            except (InvalidToken, TokenError) as e:
                logger.debug(f"JWT authentication failed: {e}")
            except Exception as e:
                logger.warning(f"Unexpected JWT auth error: {e}")
        
        # No valid authentication found
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Regular request - redirect to login
        login_url = '/login/'
        if request.path != login_url:
            login_url += f'?next={request.path}'
        
        return redirect(login_url)
    
    return wrapper
