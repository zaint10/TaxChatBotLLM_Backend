from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import W2Form

User = get_user_model()

class W2FormSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = W2Form
        fields = ('id', 'file_name', 'data')


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


class PDFUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    

class ChatSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=255)