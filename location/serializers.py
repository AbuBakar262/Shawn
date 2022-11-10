from rest_framework import serializers
from location.models import UserLocation


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