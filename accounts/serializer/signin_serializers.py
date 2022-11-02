from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User
from django.utils.translation import gettext_lazy as _


class SigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({'error': _('Invalid Credentials')})
        else:
            raise serializers.ValidationError({'error': _('Email and Password are required')})
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile_pic', 'email', 'gender', 'phone', 'instagram', 'dob', 'bio']
