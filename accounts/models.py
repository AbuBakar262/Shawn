from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

ACCOUNT_CHOICE = (
    ('Public', 'Public'),
    ('Private', 'Private')
)

ACCOUNT_TYPE = (
    ('Email', 'Email'),
    ('Instagram', 'Instagram'),
    ('Apple', 'Apple')
)


class User(AbstractUser):
    username = models.CharField(max_length=50, null=True, blank=True, unique=True)
    email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    create_profile = models.BooleanField(default=False)
    is_account = models.CharField(max_length=10, choices=ACCOUNT_CHOICE, default='Public')
    social_id = models.CharField(max_length=250, null=True, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE, default='')
    profile_pic = models.FileField(upload_to='profile_photos', null=True, blank=True)
    # profile_thumbnail = models.FileField(upload_to='profile_thumbnails', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    formatted_phone = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(_('date of birth'), null=True, blank=True)
    bio = models.TextField(_('additional information'), null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class BlockUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user', null=True, blank=True)
    block_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='block_user_by', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'block_user')

    def __str__(self):
        return f'{self.user.email} blocked {self.block_user.email}'

