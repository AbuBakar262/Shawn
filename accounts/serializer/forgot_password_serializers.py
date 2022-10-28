from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import *


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(_('Email does not exist'))
        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True,
        trim_whitespace=True,
        label=_('Password'),
        style={'input_type': 'password'},
        max_length=128
    )
    confirm_password = serializers.CharField(
        required=True,
        trim_whitespace=True,
        label=_('Password'),
        style={'input_type': 'password'},
        max_length=128
    )

    class Meta:
        model = User
        fields = ['password', 'confirm_password']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError(_('Password does not match'))
        return attrs