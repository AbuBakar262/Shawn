from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)


class CreateUserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    phone = serializers.CharField(required=False)
    instagram = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    bio = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_pic', 'gender', 'phone', 'instagram', 'dob', 'bio']
