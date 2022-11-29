from django.db.models import Q
from rest_framework import serializers
from accounts.serializers import UserSerializer
from friends_management.models import *
from django.utils.translation import gettext_lazy as _
from notification.models import *


class FriendRequestListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="sender.username")
    profile_thumbnail = serializers.FileField(source="sender.profile_thumbnail")

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'username', 'profile_thumbnail', 'message_title', 'message_body', 'type',
                  'read_status', 'created_at', 'updated_at']


FRIEND_REQUEST_STATUS = (
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected')
)


class FriendRequestActionSerializer(serializers.Serializer):
    friend_request = serializers.SlugRelatedField(queryset=Notification.objects.all(), slug_field='id', required=True)
    status = serializers.ChoiceField(choices=FRIEND_REQUEST_STATUS, required=True)
    friend_request_sender = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        friend_request = attrs.get('friend_request')
        friend_request_sender = attrs.get('friend_request_sender')
        if friend_request.type != 'Send Request':
            raise serializers.ValidationError({'error': _('This is not a friend request.')})
        if friend_request.receiver != user:
            raise serializers.ValidationError({'error': _('You are not the receiver of this friend request.')})
        if friend_request_sender != friend_request.sender:
            raise serializers.ValidationError({'error': _('This is not your friend request.')})
        if Notification.objects.filter(id=friend_request.id, sender=friend_request_sender).exists():
            raise serializers.ValidationError({'error': 'Friend request not exists!'})
        return attrs


class FriendSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'phone', 'dob', 'bio', 'email_verified',
                  'phone_verified', 'is_friend']

    def get_is_friend(self, obj):
        if Friend.objects.filter(Q(user=obj) | Q(friend=obj)).exists():
            return True
        else:
            return False


class FriendRequestSerializer(serializers.Serializer):
    friend_request = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)

    def validate(self, attrs):
        friend_request = attrs.get("friend_request")
        if Notification.objects.filter(sender=self.context['request'].user, receiver=friend_request).exists():
            raise serializers.ValidationError({'user': _('Friend request already sent')})
        if Friend.objects.filter(user=self.context['request'].user, friend=friend_request).exists():
            raise serializers.ValidationError({'user': _('You are already friends!')})

class FriendRequestDeleteSerializer(serializers.Serializer):
    friend_request_id = serializers.SlugRelatedField(queryset=Notification.objects.all(), slug_field='id', required=True)

class FriendDeleteSerializer(serializers.Serializer):
    friend_id = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)
