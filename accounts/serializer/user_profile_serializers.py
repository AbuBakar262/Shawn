from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from django.utils.translation import gettext_lazy as _


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'gender', 'contact', 'instagram', 'dob', 'bio']
