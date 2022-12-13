from django.db import models
from accounts.models import *
# Create your models here.

NOTIFICATION_TYPE = (
    ('Add Friend', 'Add Friend'),
    ('Send Request', 'Send Request'),
    ('Accept Request', 'Accept Request'),
    ('Send Message', 'Send Message')
)


class DeviceRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_device', null=True, blank=True)
    registration_id = models.CharField(max_length=250, null=True, blank=True)
    serial_no = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.registration_id}'


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_in_notification')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver_in_notification')
    message_title = models.CharField(max_length=250, null=True, blank=True)
    message_body = models.CharField(max_length=250, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE, null=True, blank=True)
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} - {self.receiver}  - {self.type}'


class SeanSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_in_sean_setting')
    notification_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
