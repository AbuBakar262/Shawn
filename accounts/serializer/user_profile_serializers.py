from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from django.utils.translation import gettext_lazy as _


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'gender', 'profile_pic', 'phone', 'instagram', 'dob',
                  'bio']

    def validate(self, attrs):
        if attrs.get('username') == '':
            attrs['username'] = None
        if User.objects.filter(username=attrs.get('username')).exclude(id=attrs.get('id')).exists():
            raise serializers.ValidationError(_("Username already exists"))
        return attrs
