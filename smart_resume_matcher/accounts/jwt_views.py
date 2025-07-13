"""
Custom JWT views for enhanced authentication
"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import CustomTokenObtainPairSerializer, UserProfileSerializer

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that returns enhanced user information
    """
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT refresh view that includes updated user information
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get the refresh token from request
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    # Decode the refresh token to get user info
                    refresh = RefreshToken(refresh_token)
                    user_id = refresh.get('user_id')
                    
                    if user_id:
                        user = User.objects.get(id=user_id)
                        serializer = UserProfileSerializer(user)
                        response.data['user'] = serializer.data
                except Exception:
                    # If we can't get user info, just return the tokens
                    pass
        
        return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def logout_view(request):
    """
    JWT logout view that blacklists the refresh token
    """
    try:
        # Try multiple possible field names for the refresh token
        refresh_token = (
            request.data.get('refresh_token') or 
            request.data.get('refresh') or
            request.data.get('refreshToken')
        )
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({
                    'message': 'Successfully logged out'
                }, status=status.HTTP_200_OK)
            except Exception as blacklist_error:
                # If blacklisting fails, still return success
                # The token will expire naturally
                return Response({
                    'message': 'Successfully logged out',
                    'note': 'Token will expire naturally'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Logout failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    Get current user profile information
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token_view(request):
    """
    Verify JWT token and return user information
    """
    serializer = UserProfileSerializer(request.user)
    return Response({
        'valid': True,
        'user': serializer.data
    })
