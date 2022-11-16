from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from accounts.models import *


class AdminLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(email=email.lower(), password=password)
            if user:
                if user.is_active:
                    if user.is_superuser:
                        attrs['user'] = user
                    else:
                        raise serializers.ValidationError({'error': _('User is not admin')})
                else:
                    raise serializers.ValidationError({'error': _('User is not active')})
            else:
                raise serializers.ValidationError({'error': _('Invalid credentials')})
        else:
            raise serializers.ValidationError({'error': _('Must provide email and password')})
        return attrs
