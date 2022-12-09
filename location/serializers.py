from rest_framework import serializers
from location.models import *
from django.utils.translation import gettext_lazy as _
from accounts.serializers import *


class UserLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    address = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = FavouriteLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'title', 'image', 'created_at', 'updated_at']

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")
        if FavouriteLocation.objects.filter(latitude=latitude, longitude=longitude, user=self.context['request'].user).exists():
            raise serializers.ValidationError({'error': _('You already save this location')})
        return attrs


class UserLocationListSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = FavouriteLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'title', 'image', 'created_at', 'updated_at',
                  'total']

    def get_total(self, obj):
        if CheckInLocation.objects.filter(latitude=obj.latitude, longitude=obj.longitude).exists():
            total = CheckInLocation.objects.filter(latitude=obj.latitude, longitude=obj.longitude).count()
            return total
        else:
            total = 0
            return total


class CheckInLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    address = serializers.CharField(required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = CheckInLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'title', 'created_at', 'updated_at']

    def validate(self, attrs):
        user = self.context['request'].user
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        address = attrs.get('address')
        if CheckInLocation.objects.filter(user=user, latitude=latitude, longitude=longitude, address=address).exists():
            raise serializers.ValidationError({'error': _('You already check in this location')})
        return attrs


class CheckInListLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckInLocation
        fields = ['id', 'user', 'latitude', 'longitude', 'address', 'title', 'created_at', 'updated_at']


class SearchLocationSerializer(serializers.Serializer):
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
