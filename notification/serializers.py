from rest_framework import serializers
from .models import *
from accounts.serializers import UserSerializer


class DeviceRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)
    registration_id = serializers.CharField(required=True)
    serial_no = serializers.CharField(required=False)

    class Meta:
        model = DeviceRegistration
        fields = ['id', 'user', 'registration_id', 'serial_no', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data
