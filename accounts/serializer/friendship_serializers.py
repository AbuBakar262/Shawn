from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User, FriendRequest, Friend
from django.utils.translation import gettext_lazy as _
from accounts.serializer.signin_serializers import *


class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ['friend', 'created_at', 'modified_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['friend'] = UserSerializer(instance.friend).data
        representation['friend_count'] = Friend.objects.filter(user=instance.user).count()
        return representation