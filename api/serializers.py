from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import W2Form

User = get_user_model()

class W2FormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = W2Form
        fields = ('id', 'file_name', 'data')

class W2FormSensitiveInfoSerializer(serializers.ModelSerializer):
    decrypted_ssn = serializers.CharField(read_only=True)
    class Meta:
        model = W2Form
        fields = ['decrypted_ssn']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['decrypted_ssn'] = instance.decrypted_ssn
        return data


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]  # Extract username from email
        user = User.objects.create_user(username=username, **validated_data)
        return user


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {
            'email': {'read_only': True},
            'is_2fa_enabled': {'read_only': True},
        }
        fields = ['id', 'email', 'username', 'date_joined', 'is_active', 'is_superuser', 'is_staff', 'is_2fa_enabled']
        

class PDFUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    

class ChatSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255)
    
class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()