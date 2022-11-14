from datetime import date
import django.contrib.auth.password_validation as validators
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


class SignupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, label='Password', style={'input_type': 'password'},
                                     write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'password']

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': _('Email already exists')})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': _('Username already exists')})
        if len(data['username']) > 15:
            raise serializers.ValidationError({'username': _('Username must be less than 15 characters')})
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        with transaction.atomic():
            user = User.objects.create(username=username, email=email, password=make_password(password),
                                       account_type="Email")
            user.save()
            if validated_data.get('registration_id'):
                FireBaseNotification.objects.create(user=user, registration_id=validated_data['registration_id'])
        return user


class SocialSignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    instagram = serializers.CharField(required=False)
    apple = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']

    def validate(self, attrs):
        username = attrs.get("username")
        instagram = attrs.get("instagram")
        apple = attrs.get("apple")
        email = attrs.get("email")
        if not instagram and not apple:
            raise serializers.ValidationError({'error': _('instagram or apple one is required')})
        if instagram:
            if User.objects.filter(instagram=instagram).exists():
                raise serializers.ValidationError({'instagram': _('instagram already exists')})
        if apple:
            if User.objects.filter(apple=apple).exists():
                raise serializers.ValidationError({'apple': _('apple already exists')})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _('username already exists')})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': _('email already exists')})
        if len(username) > 15:
            raise serializers.ValidationError({'username': _('Username must be less than 15 characters')})
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        with transaction.atomic():
            if "instagram" in validated_data:
                instagram = validated_data['instagram']
                user = User.objects.create(username=username, instagram=instagram, account_type="Instagram")
                user.save()
            if "apple" in validated_data:
                apple = validated_data['apple']
                user = User.objects.create(username=username, apple=apple, account_type="Apple")
                user.save()
            if validated_data.get('registration_id'):
                FireBaseNotification.objects.create(user=user, registration_id=validated_data['registration_id'])
        return user


class SocialLoginSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    username = serializers.CharField(required=False)
    instagram = serializers.CharField(required=False)
    apple = serializers.CharField(required=False)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']

    def validate(self, attrs):
        # username = attrs.get("username")
        apple = attrs.get("apple")
        instagram = attrs.get("instagram")
        if not instagram and not apple:
            raise serializers.ValidationError({'error': _('instagram or apple one is required')})
        # if not User.objects.filter(username=username).exists():
        #     raise serializers.ValidationError({'username': _('username does not exists')})
        if instagram:
            if not User.objects.filter(instagram=instagram).exists():
                raise serializers.ValidationError({'unauthorized': _('Invalid credentials')})
            else:
                user = User.objects.filter( instagram=instagram).first()
                return user
        else:
            if not User.objects.filter(apple=apple).exists():
                raise serializers.ValidationError({'unauthorized': _('Invalid credentials')})
            else:
                user = User.objects.filter(apple=apple).first()
                return user


class CreateUserProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    profile_pic = serializers.FileField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']

    def validate(self, attrs):
        dob = attrs.get("dob")
        if User.objects.filter(id=self.context['instance'].id, create_profile=True).exists():
            raise serializers.ValidationError({'error': _('profile already created')})
        if dob:
            age = relativedelta(date.today(), dob).years
            if age < 16:
                raise serializers.ValidationError(
                    {'dob': _("You must be 16 or older to use Sean APP")})
        if User.objects.filter(phone=attrs.get("phone")).exists():
            raise serializers.ValidationError(
                {'phone': _("Phone number already exists")})
        return attrs


class SocialUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']


class SocialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']


class SigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        username = attrs.get('username')
        if username:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError({'username': _('username does not exists')})
            else:
                user_email = User.objects.filter(username=username).first().email
                user = authenticate(email=user_email, password=password)
                if not user:
                    raise serializers.ValidationError({'error': _('Invalid credentials')})

        if email and password:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'email': _('email does not exists')})
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({'error': _('Invalid credentials')})
        return user


class ForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'phone']

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        if email is None and phone is None:
            raise serializers.ValidationError({'error': _('Email or Phone is required, Please enter one of them')})
        if email:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError({'error': _('Email does not exist')})
        if phone:
            if not User.objects.filter(phone=phone).exists():
                raise serializers.ValidationError({'error': _('Phone does not exist')})
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)
    otp = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.ModelSerializer):
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


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockUser
        fields = ['block_user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['block_user'] = UserSerializer(instance.block_user).data
        return data


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'create_profile','instagram', 'apple', 'is_account', 'profile_pic',
                  'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'account_type']
