from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)