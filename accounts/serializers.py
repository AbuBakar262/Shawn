from rest_framework import serializers
from accounts.models import User, FireBaseNotification
from django.utils.translation import gettext_lazy as _
import django.contrib.auth.password_validation as validators
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic', 'email', 'gender', 'phone', 'instagram',
                  'dob', 'bio', 'create_profile', 'is_account']


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, label='Password', style={'input_type': 'password'},
                                     write_only=True)
    registration_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'registration_id']

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': _('Email already exists')})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': _('Username already exists')})
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        with transaction.atomic():
            user = User.objects.create(username=username, email=email, password=make_password(password))
            user.save()
            if validated_data.get('registration_id'):
                FireBaseNotification.objects.create(user=user, registration_id=validated_data['registration_id'])
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance).data
        return representation


class SocialSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    instagram = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic', 'email', 'gender', 'phone', 'instagram',
                  'dob', 'bio', 'create_profile']

    # def validate(self, data):
    #     if User.objects.filter(email=data['email']).exists():
    #         raise serializers.ValidationError({'email': _('Email already exists')})
    #     if User.objects.filter(username=data['username']).exists():
    #         raise serializers.ValidationError({'username': _('Username already exists')})
    #     if User.objects.filter(instagram=data['instagram']).exists():
    #         raise serializers.ValidationError({'instagram': _('Instagram already exists')})
    #     return data

    def create(self, validated_data):
        if not User.objects.filter(email=validated_data['email'], instagram=validated_data['instagram']).exists():
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                instagram=validated_data['instagram'],
            )
            return user
        else:
            user = User.objects.get(email=validated_data['email'], instagram=validated_data['instagram'])
            return user


class CreateUserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.FileField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone = serializers.CharField(required=True)
    instagram = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_pic', 'gender', 'phone', 'instagram', 'dob', 'bio']


class SocialCreateUserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.FileField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_pic', 'gender', 'phone', 'instagram', 'dob', 'bio']


class SigninSerializer(serializers.ModelSerializer):
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
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({'error': _('Invalid credentials')})
        attrs['user'] = user
        return attrs


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


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)
    profile_pic = serializers.FileField(required=True)

    class Meta:
        model = User
        fields = ['username', 'gender', 'dob', 'bio', 'profile_pic']

    def validate(self, attrs):
        username = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _('Username already exists')})
        return attrs
