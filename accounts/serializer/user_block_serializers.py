from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User, BlockUser
from accounts.serializer.signin_serializers import *
from django.utils.translation import gettext_lazy as _


# block/unblock user serializer for user
class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockUser
        fields = ['blocked_user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['blocked_user'] = UserSerializer(instance.blocked_user).data
        return data
