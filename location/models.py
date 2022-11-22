from django.db import models
from accounts.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.


class FavouriteLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_location', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} location'


class CheckInLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='check_in_location', null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'The location of {self.user} is {self.address}'
