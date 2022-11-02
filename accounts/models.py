from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

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
