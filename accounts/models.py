from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from baselayer.basemodels import LogsMixin

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


class User(AbstractUser):
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    profile_pic = models.FileField(upload_to='media/profile_photos', null=True, blank=True)
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=256, null=True, blank=True)
    dob = models.DateField(_('date of birth'), null=True, blank=True)
    bio = models.TextField(_('additional information'), null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    create_profile = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class VerificationCode(LogsMixin):
    """VerificationCode model for storing verification code information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.code}'


FRIEND_REQUEST_STATUS = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected')
)


class FriendRequest(LogsMixin):
    """FriendRequest model for storing friend request information"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_STATUS, default='pending')

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender} sent friend request to {self.receiver}'


class Friend(LogsMixin):
    """Friend model for storing friend information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend')

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f'{self.user} is friend with {self.friend}'


class BlockUser(LogsMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_user')
    block_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'blocked_user')

    def __str__(self):
        return f'{self.user} blocked {self.blocked_user}'


class Location(LogsMixin):
    """Location model for storing location information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_user')
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.user} location is {self.city}, {self.country}'
