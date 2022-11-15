from django.db import models
from accounts.models import *
# Create your models here.


class DeviceRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_device', null=True, blank=True)
    registration_id = models.CharField(max_length=250, null=True, blank=True)
    serial_no = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.registration_id}'