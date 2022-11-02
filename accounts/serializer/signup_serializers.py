from rest_framework import serializers
from accounts.models import *
from django.utils.translation import gettext_lazy as _
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator
from accounts.serializer.signin_serializers import UserSerializer

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, label='Password', style={'input_type': 'password'},
                                     write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(_('Email already exists'))
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(_('Username already exists'))
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
        )
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance).data
        return representation


class VerifySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)

    class Meta:
        model = VerificationCode
        fields = ['email', 'code']

    def validate(self, attrs):
        if not VerificationCode.objects.filter(user__email=attrs['email'], code=attrs['code']).exists():
            raise serializers.ValidationError({'code': 'Invalid code'})
        return attrs

    def create(self, validated_data):
        user = User.objects.get(email=validated_data['email'])
        user.is_verified = True
        user.save()
        return user
