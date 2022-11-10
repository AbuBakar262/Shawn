from rest_framework import serializers
from accounts.serializers import UserSerializer
from accounts.models import User
from location.models import UserLocation
from django.utils.translation import gettext_lazy as _
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


class UserLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    address = serializers.CharField(required=True)

    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'created_at', 'updated_at']


class UserLocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'created_at', 'updated_at']