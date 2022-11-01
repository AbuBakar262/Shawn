from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User, Location
from accounts.serializer.signin_serializers import *
from django.utils.translation import gettext_lazy as _


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['user', 'ip_address', 'latitude', 'longitude', 'city', 'country']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data
