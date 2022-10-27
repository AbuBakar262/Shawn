from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from baselayer.basemodels import LogsMixin

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)


class User(AbstractUser):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    contact = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(_('date of birth'), null=True, blank=True)
    bio = models.TextField(_('additional information'), null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class VerificationCode(LogsMixin):
    """VerificationCode model for storing verification code information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, null=True, blank=True)
    is_expired = models.BooleanField(default=False)