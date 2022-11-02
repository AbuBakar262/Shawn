from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User, Location
from accounts.serializer.signin_serializers import *
from django.utils.translation import gettext_lazy as _


class LocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'city', 'country')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation


class UserLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'latitude', 'longitude', 'city', 'country')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        return representation