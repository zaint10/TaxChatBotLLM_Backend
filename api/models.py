import os
import pyotp
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from cryptography.fernet import Fernet

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    secret_key = models.CharField(max_length=50, null=True, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    otp_retry_count = models.IntegerField(default=0)
    lockout_time = models.DateTimeField(null=True, blank=True)
    last_otp_time = models.DateTimeField(null=True, blank=True)
    
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def save(self, *args, **kwargs):
        if not self.secret_key:
            self.secret_key = self.generate_secret_key()
        
        super().save(*args, **kwargs)
    
    def generate_secret_key(self):
        return pyotp.random_base32()
    
    @property
    def has_completed_2fa(self):
        return self.is_2fa_enabled


def empty_list():
        return '[]'

class W2Form(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file_name = models.CharField(blank=False, null=True)
    data = models.TextField(blank=True, null=True)
    messages = models.JSONField(blank=True, default=empty_list)
    employee_ssn = models.BinaryField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.employee_ssn:
            key = os.environ.get("ENCRYPTION_KEY").encode()
            cipher_suite = Fernet(key)
            encrypted_ssn = cipher_suite.encrypt(self.employee_ssn.encode())
            self.employee_ssn = encrypted_ssn
        super().save(*args, **kwargs)

    @property
    def decrypted_ssn(self):
        if self.employee_ssn:
            key = os.environ.get("ENCRYPTION_KEY").encode()
            cipher_suite = Fernet(key)
            decrypted_ssn = cipher_suite.decrypt(bytes(self.employee_ssn)).decode()
            return decrypted_ssn
        return None

    def __str__(self):
        return f"W2Form for {self.user.username}"


