import pyotp
import base64
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login

from .serializers import UserSerializer, OTPVerificationSerializer, ListUserSerializer
import qrcode
from io import BytesIO

class SignupAPIView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': ListUserSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            return Response({'error': 'Please check your credentials (Email or password)'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class QRCodeAPIView(APIView):
    def get(self, request):
        # Retrieve the user's secret key
        secret_key = request.user.secret_key
        if not secret_key:
            request.user.save()
        
        # Generate a TOTP object
        totp = pyotp.totp.TOTP(secret_key)
        
        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(request.user.email, issuer_name='TaxChatBotLLM')
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Create a BytesIO object to store the QR code image
        qr_code_image = BytesIO()
        qr.make_image().save(qr_code_image, format='PNG')
        
        # Base64 encode the image data
        qr_code_image_base64 = base64.b64encode(qr_code_image.getvalue()).decode('utf-8')
        
        # Construct the HTML response with the QR code image
        html_response = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QR Code</title>
        </head>
        <body>
            <h1>Scan QR Code</h1>
            <img src="data:image/png;base64,{qr_code_image_base64}" alt="QR Code">
        </body>
        </html>
        '''
        
        # Return the HTML response
        return Response({"qr_code_value": provisioning_uri})


class OTPVerificationAPIView(APIView):
    serializer_class = OTPVerificationSerializer
    # Constants for OTP expiration and retry limits
    OTP_EXPIRATION_TIME = timedelta(minutes=1)
    MAX_OTP_RETRIES = 3
    LOCKOUT_DURATION = timedelta(minutes=5)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Check if user is already locked out due to exceeding retry limits
            if request.user.lockout_time and request.user.lockout_time > timezone.now() and request.user.otp_retry_count == self.MAX_OTP_RETRIES:
                time_remaining = request.user.lockout_time - timezone.now()
                return Response({'error': f'Account locked. Try again in {time_remaining.seconds // 60} minutes.'}, status=status.HTTP_403_FORBIDDEN)
            elif request.user.otp_retry_count == self.MAX_OTP_RETRIES:
                request.user.otp_retry_count = 0
                request.user.save()
            
            otp = serializer.validated_data.get('otp')
            
            
            # Check if OTP matches
            secret_key = request.user.secret_key
            if not secret_key:
                return Response({'error': 'Secret key not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            totp = pyotp.TOTP(secret_key)
            if not totp.verify(otp):
                 # Increment retry count
                request.user.otp_retry_count += 1
                request.user.save()
                
                 # Check if user has exceeded retry limits
                if request.user.otp_retry_count >= self.MAX_OTP_RETRIES:
                    # Lock the account for a specified duration
                    request.user.lockout_time = timezone.now() + self.LOCKOUT_DURATION
                    request.user.save()
                    
                    return Response({'error': 'Too many failed attempts. Account locked.'}, status=status.HTTP_403_FORBIDDEN)
                
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.user.is_2fa_enabled:
                request.user.is_2fa_enabled = True
                request.user.save()
            
            return Response({'message': 'OTP verification successful'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
