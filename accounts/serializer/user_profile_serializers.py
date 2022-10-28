from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from django.utils.translation import gettext_lazy as _


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'gender', 'contact', 'instagram', 'dob', 'bio']

    def validate(self, attrs):
        if not attrs.get('first_name').isalpha():
            raise serializers.ValidationError(_('First Name must be alphabetical'))
        if not attrs.get('last_name').isalpha():
            raise serializers.ValidationError(_('Last Name must be alphabetical'))
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        return attrs
