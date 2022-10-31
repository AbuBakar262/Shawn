from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User, FriendRequest, Friend
from django.utils.translation import gettext_lazy as _
from accounts.serializer.signin_serializers import *


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=False)
    receiver = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=False)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'modified_at']

    def validate(self, attrs):
        sender = attrs.get('sender')
        receiver = attrs.get('receiver')
        if sender == receiver:
            raise serializers.ValidationError(_("You can't send friend request to yourself"))
        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError(_("You have already sent friend request to this user"))
        if FriendRequest.objects.filter(sender=receiver, receiver=sender).exists():
            raise serializers.ValidationError(_("You have already received friend request from this user"))
        if Friend.objects.filter(user=sender, friend=receiver).exists():
            raise serializers.ValidationError(_("You are already friend with this user"))
        return attrs


class FriendRequestActionSerializer(serializers.ModelSerializer):
    friend_request_id = serializers.SlugRelatedField(queryset=FriendRequest.objects.all(), slug_field='id', required=False)
    status = serializers.CharField(max_length=10)

    class Meta:
        model = FriendRequest
        fields = ['friend_request_id', 'status']

    def validate(self, attrs):
        status = attrs.get('status')
        friend_request_id = attrs.get('friend_request_id')
        if not status in ['accepted', 'rejected']:
            raise serializers.ValidationError(_("Status must be accepted or rejected"))
        if not friend_request_id.status == 'pending':
            raise serializers.ValidationError(_("Friend request is already {}").format(friend_request_id.status))
        return attrs


class FriendRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'modified_at']

        # get send profile data
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender'] = UserSerializer(instance.sender).data
        representation['friend_request_count'] = FriendRequest.objects.filter(receiver=instance.receiver,
                                                                                status='pending').count()
        return representation

