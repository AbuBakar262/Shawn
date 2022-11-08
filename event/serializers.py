from django.utils.translation import gettext_lazy as _
import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework import serializers
from accounts.serializers import UserSerializer
from accounts.models import User
from event.models import Event


class EventSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)
    address = serializers.CharField(required=True)

    class Meta:
        model = Event
        fields = ['id', 'user', 'title', 'description', 'start_date', 'end_date', 'address', 'created_at', 'updated_at']


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'title', 'description', 'start_date', 'end_date', 'address', 'created_at', 'updated_at']


class UpdateEventSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    photo = serializers.FileField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    address = serializers.CharField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    is_hide = serializers.BooleanField(required=False)

    class Meta:
        model = Event
        fields = ['id', 'user', 'title', 'description', 'photo', 'latitude', 'longitude', 'address', 'start_date', 'end_date', 'is_hide', 'created_at', 'updated_at']
