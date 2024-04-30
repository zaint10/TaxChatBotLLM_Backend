from functools import wraps
import pyotp
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

def require_2fa(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        # Check if the user has completed 2FA authentication
        if not request.user.has_completed_2fa:
            return Response({'error': '2FA authentication required'}, status=HTTP_403_FORBIDDEN)
        
        # Check if OTP verification is successful
        otp = request.data.get('otp') or request.headers.get('X-OTP')
        if not otp:
            return Response({'error': 'OTP is required'}, status=HTTP_400_BAD_REQUEST)
        
        secret_key = request.user.secret_key
        if not secret_key:
            return Response({'error': 'Secret key not found'}, status=HTTP_400_BAD_REQUEST)
        
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(otp):
            return Response({'error': 'Invalid OTP'}, status=HTTP_403_FORBIDDEN)
        
        return func(view, request, *args, **kwargs)
    return wrapper