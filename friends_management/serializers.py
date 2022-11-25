from django.db.models import Q
from rest_framework import serializers
from accounts.serializers import UserSerializer
from friends_management.models import *
from django.utils.translation import gettext_lazy as _

FRIEND_REQUEST_STATUS = (
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected')
)


class FriendRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'user', 'receiver_friend_request', 'status', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user).data
        representation['total'] = FriendRequest.objects.filter(receiver_friend_request=instance.receiver_friend_request,
                                                                              status='pending').count()
        return representation


class FriendRequestActionSerializer(serializers.ModelSerializer):
    friend_request = serializers.SlugRelatedField(queryset=FriendRequest.objects.all(), slug_field='id', required=True)
    status = serializers.ChoiceField(choices=FRIEND_REQUEST_STATUS, required=True)

    class Meta:
        model = FriendRequest
        fields = ['friend_request', 'status']

    def validate(self, attrs):
        status = attrs.get('status')
        friend_request_id = attrs.get('friend_request')
        if not status in ['accepted', 'rejected']:
            raise serializers.ValidationError(_("Status must be accepted or rejected"))
        if not friend_request_id.status == 'pending':
            raise serializers.ValidationError(_("Friend request is already {}").format(friend_request_id.status))
        return attrs


class FriendSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'is_friend']

    def get_is_friend(self, obj):
        if Friend.objects.filter(Q(user=obj) | Q(friend=obj)).exists():
            return True
        else:
            return False
