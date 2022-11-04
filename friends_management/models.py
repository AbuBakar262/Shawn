from django.db import models
from accounts.models import User

# Create your models here.


FRIEND_REQUEST_STATUS = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected')
)


class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', null=True, blank=True)
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_STATUS, default='pending', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender} sent friend request to {self.receiver}'


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} is friend with {self.friend}'


class RejectRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reject', null=True, blank=True)
    rejected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rejected_user', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} rejected {self.rejected_user}'
