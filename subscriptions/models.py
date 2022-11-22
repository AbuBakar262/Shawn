from django.db import models
from accounts.models import User

# Create your models here.

SUBSCRIPTION_STATUS = (
    ('Subscribed', 'Subscribed'),
    ('Unsubscribed', 'Unsubscribed'),
    ('Trial', 'Trial'),
    ('Expired', 'Expired'),
)

SUBSCRIPTION_PERIOD = (
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly'),
)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_user', null=True, blank=True)
    subscription_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, null=True, blank=True)
    period = models.CharField(max_length=20, choices=SUBSCRIPTION_PERIOD, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} is {self.status} with {self.period}'
