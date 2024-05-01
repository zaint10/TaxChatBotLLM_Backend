"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import auth, views
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'', views.W2FormViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', auth.SignupAPIView.as_view()),
    path('login/', auth.LoginAPIView.as_view()),
    path('users/me', auth.CurrentUserAPIView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get-qr-code/', auth.QRCodeAPIView.as_view(), name='get_qr_code'),
    path('verify-qr-code-otp/', auth.OTPVerificationAPIView.as_view(), name='verify_qr_code_otp/'),
    path('upload/', views.W2FormUpload.as_view(), name='w2_form_upload'),
    path('chat/<int:w2form_id>', views.ChatView.as_view(), name='w2_chat_view'),
    path('w2form/', include(router.urls)),
    path('w2form/<int:w2form_id>/sensitive-info/', views.W2FormSensitiveInfoAPIView.as_view(), name='w2form-sensitive-info'),
]
