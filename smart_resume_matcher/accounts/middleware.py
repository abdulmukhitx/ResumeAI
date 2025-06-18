"""
JWT Authentication Middleware for Django Views
This middleware authenticates users based on JWT tokens in the Authorization header
or in localStorage (handled by frontend), allowing regular Django views to work with JWT.
"""

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users with JWT tokens for Django views.
    This allows @login_required decorators to work with JWT authentication.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.jwt_auth = JWTAuthentication()
    
    def process_request(self, request):
        """
        Process the request and authenticate user if JWT token is present.
        """
        # Skip if user is already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
        
        # Try to authenticate with JWT from multiple sources
        token = None
        
        try:
            # 1. Try Authorization header first (for API calls)
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if not auth_header:
                auth_header = request.META.get('HTTP_X_AUTHORIZATION')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            # 2. Try cookies (for browser navigation) - PRIMARY FIX
            elif 'access_token' in request.COOKIES:
                token = request.COOKIES['access_token']
                logger.debug("Found JWT token in cookies")
            
            # 3. Try custom header (some AJAX setups)
            elif request.META.get('HTTP_X_ACCESS_TOKEN'):
                token = request.META.get('HTTP_X_ACCESS_TOKEN')
            
            # 4. Try URL parameter (fallback, not recommended)
            elif request.GET.get('access_token'):
                token = request.GET.get('access_token')
                logger.debug("Found JWT token in URL parameters")
            
            if token:
                # Use DRF's JWT authentication to validate token
                validated_token = self.jwt_auth.get_validated_token(token)
                user = self.jwt_auth.get_user(validated_token)
                
                if user and user.is_active:
                    # Set the user on the request
                    request.user = user
                    logger.info(f"✅ JWT authentication successful for user: {user.email}")
                    return None
            
        except (InvalidToken, TokenError, AttributeError) as e:
            logger.debug(f"JWT authentication failed: {e}")
            # Token is invalid or expired, continue as anonymous
            pass
        except Exception as e:
            logger.warning(f"Unexpected error in JWT authentication: {e}")
            pass
        
        # If no valid JWT token, keep user as anonymous
        # This allows the normal authentication flow to continue
        return None
