from django.db import models
from accounts.models import User


STATUS_CHOICES = (
    ('subscribed', 'Subscribed'),
    ('unsubscribed', 'Unsubscribed'),
    ('trial', 'Trial'),
)


class ReportUser(models.Model):
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by')
    reported_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_at')
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.reported_by.email} reported to {self.reported_to.email}'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    is_blocked = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unsubscribed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
