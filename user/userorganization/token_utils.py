from rest_framework_simplejwt.tokens import AccessToken, TokenError,RefreshToken
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
# from user.userorganization.token_utils import generate_access_token
def generate_access_token(user):
    access_token = AccessToken.for_user(user)
    refresh = RefreshToken.for_user(user)
    # Example of adding custom claims
    access_token['userId'] = str(user.userId)
    access_token['email'] = user.email
    access_token['issued_at'] = timezone.now().timestamp()
    access_token['expiry'] = access_token['exp']
    return str(access_token)



#decoding
def decode_access_token(token):
    try:
        access_token = AccessToken(token)
        return {
            'userId': access_token['userId'],
            'email': access_token['email'],
            'issued_at': access_token['issued_at'],
            'expiry': access_token['exp'],
        }
    except TokenError as e:
        if isinstance(e, TokenError.TokenExpired):
            return Response({
                'status': 'error',
                'message': 'Token has expired.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        elif isinstance(e, TokenError):
            return Response({
                'status': 'error',
                'message': 'Token is invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'error',
                'message': 'Token error occurred.'
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        print(f"Unexpected error occurred: {e}")
        return None

