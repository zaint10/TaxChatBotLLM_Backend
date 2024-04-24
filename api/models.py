from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


# Create your models here.
class W2Form(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"W2Form for {self.user.username}"