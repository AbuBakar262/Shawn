from django.db import models
from accounts.models import User


# Create your models here.


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_location', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
