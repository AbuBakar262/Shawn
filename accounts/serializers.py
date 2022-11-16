from datetime import date
import django.contrib.auth.password_validation as validators
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from notification.models import DeviceRegistration
from .models import *
from .utils import delete_image, social_login


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

ACCOUNT_CHOICE = (
    ('Public', 'Public'),
    ('Private', 'Private')
)


class SignupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, label='Password', style={'input_type': 'password'},
                                     write_only=True)
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'password', 'device_id']

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email'].lower()).exists():
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
        device_id = validated_data['device_id']
        with transaction.atomic():
            user = User.objects.create(username=username, email=email.lower(), password=make_password(password),
                                       account_type="Email")
            user.save()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
        return user


class SocialSignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    instagram = serializers.CharField(required=False)
    apple = serializers.CharField(required=False)
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'device_id']

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
        if User.objects.filter(email=email.lower()).exists():
            raise serializers.ValidationError({'email': _('email already exists')})
        if len(username) > 15:
            raise serializers.ValidationError({'username': _('Username must be less than 15 characters')})
        return attrs

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        device_id = validated_data['device_id']
        with transaction.atomic():
            if "instagram" in validated_data:
                instagram = validated_data['instagram']
                user = User.objects.create(username=username, instagram=instagram, email=email.lower(), account_type="Instagram")
                user.save()
            if "apple" in validated_data:
                apple = validated_data['apple']
                user = User.objects.create(username=username, apple=apple, email=email.lower(), account_type="Apple")
                user.save()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
        return user


class SocialLoginSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    username = serializers.CharField(required=False)
    instagram = serializers.CharField(required=False)
    apple = serializers.CharField(required=False)
    email = serializers.CharField(required=True)
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'device_id']

    def validate(self, attrs):
        email = attrs.get("email")
        apple = attrs.get("apple")
        instagram = attrs.get("instagram")
        device_id = attrs.get('device_id')
        # When user Login, device_id will be saved in DeviceRegistration table
        data = social_login(email=email.lower(), apple=apple, instagram=instagram, device_id=device_id)
        return data


def image_validator(file):
    max_file_size = 1024 * 1024 * 5  # 5MB
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is 5MB'))


class CreateUserProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    profile_pic = serializers.FileField(validators=[image_validator], required=True)
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
    email = serializers.CharField(required=True)
    # username = serializers.CharField(required=False)
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified', 'password', 'device_id']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        device_id = attrs.get('device_id')
        if User.objects.filter(username=email).exists():
            user_email = User.objects.filter(username=email).first().email
            user = authenticate(email=user_email.lower(), password=password)
        else:
            user = authenticate(email=email.lower(), password=password)
        if not user:
            raise serializers.ValidationError({'error': _('Invalid credentials')})
        if not user.is_active:
            raise serializers.ValidationError({'error': _('Account Disabled, contact admin')})
        device = DeviceRegistration.objects.filter(user=user)
        if not device.exists():
            DeviceRegistration.objects.create(user=user, registration_id=device_id)
        if not device.filter(registration_id=device_id).exists():
            DeviceRegistration.objects.filter(user=user).update(registration_id=device_id)
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
            if not User.objects.filter(email=email.lower()).exists():
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
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    phone = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    bio = serializers.CharField(required=False)
    profile_pic = serializers.FileField(required=False)
    instagram = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'apple', 'instagram', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'phone', 'dob', 'bio', 'email_verified', 'phone_verified']

    def validate(self, attrs):
        phone = attrs.get('phone')
        profile_pic = attrs.get('profile_pic')
        user = self.context['request'].user
        if User.objects.filter(phone=phone).exclude(is_superuser=True).exclude(id=user.id).exists():
            raise serializers.ValidationError({'phone': _('phone already exists')})
        profile = User.objects.filter(id=user.id).first().profile_pic
        if not profile.name.split("profile_photos/")[1] == profile_pic:
            delete_image(profile=profile)
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


class UserProfileStatusSerializer(serializers.ModelSerializer):
    is_account = serializers.ChoiceField(choices=ACCOUNT_CHOICE, required=True)

    class Meta:
        model = User
        fields = ['is_account']