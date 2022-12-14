from datetime import date
import django.contrib.auth.password_validation as validators
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from notification.models import DeviceRegistration
from .models import *
from .utils import *
from friends_management.models import *


class UserSerializer(serializers.ModelSerializer):
    profile_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone',
                  'dob', 'bio', 'email_verified', 'phone_verified', 'instagram_profile']

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

ACCOUNT_CHOICE = (
    ('Public', 'Public'),
    ('Private', 'Private')
)
SOCIAL_ACCOUNT_TYPE = (
    ('Instagram', 'Instagram'),
    ('Apple', 'Apple')
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
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio', 'email_verified',
                  'phone_verified', 'password','device_id', 'instagram_profile']

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if User.objects.filter(email=data['email'].lower()).exists():
            raise serializers.ValidationError({'email': _('Email already exists')})
        if User.objects.filter(username=data['username'].lower()).exists():
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
            user = User.objects.create(username=username.lower(), email=email.lower(), password=make_password(password),
                                       account_type="Email")
            user.save()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
        return user


def image_validator(file):
    max_file_size = 1024 * 1024 * 5  # 5MB
    if file.size > max_file_size:
        raise serializers.ValidationError(_('Max file size is 5MB'))


class SocialLoginSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    username = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    social_id = serializers.CharField(required=True)
    instagram_profile = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=True)
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)
    account_type = serializers.ChoiceField(choices=SOCIAL_ACCOUNT_TYPE, required=True, allow_null=True,
                                           allow_blank=True)
    profile_pic = serializers.FileField(validators=[image_validator], required=False)
    profile_thumbnail = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    formatted_phone = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    country_code = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    dob = serializers.DateField(required=False)
    bio = serializers.CharField(required=True, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone',
                  'dob', 'bio', 'email_verified', 'phone_verified', 'device_id', 'instagram_profile']

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        social_id = validated_data['social_id']
        device_id = validated_data['device_id']
        account_type = validated_data['account_type']
        gender = validated_data['gender']
        phone = validated_data['phone']
        formatted_phone = validated_data['formatted_phone']
        country_code = validated_data['country_code']
        bio = validated_data['bio']
        instagram_profile = validated_data['instagram_profile']
        with transaction.atomic():
            if User.objects.filter(social_id=social_id, username=username.lower()).exists() \
                    or User.objects.filter(social_id=social_id, email=email.lower()).exists():
                data = social_login(username, social_id, device_id, email)
                return data
            else:
                if User.objects.filter(email=email.lower()).exists():
                    message = ['Email already exists']
                    raise serializers.ValidationError({'email': message})
                if User.objects.filter(username=username.lower()).exists():
                    message = ['username already exists']
                    raise serializers.ValidationError({'username': message})
                if User.objects.filter(social_id=social_id).exists():
                    message = ['social_id already exists']
                    raise serializers.ValidationError({'social_id': message})
                if User.objects.filter(phone=phone).exists():
                    message = ['Phone already exists']
                    raise serializers.ValidationError({'phone': message})
                if instagram_profile:
                    if not instagram_profile.startswith(
                            ('https://www.instagram.com', 'www.instagram.com', 'instagram.com')):
                        message = ['please enter a valid instagram profile url!']
                        raise serializers.ValidationError(
                            {'instagram_profile': message})
                dob = validated_data['dob']
                if dob:
                    age = relativedelta(date.today(), dob).years
                    if age < 16:
                        raise serializers.ValidationError(
                            {'dob': _("You must be 16 or older to use Sean App")})
                # if 'profile_thumbnail' not in validated_data:
                #     profile_thumbnail = None
                # else:
                #     profile_thumbnail = validated_data['profile_thumbnail']

                if 'profile_pic' not in validated_data:
                    raise serializers.ValidationError({'profile_pic': [
                        "The submitted data was not a file. Check the encoding type on the form."
                    ]})

                user = User.objects.create(username=username.lower(), social_id=social_id, email=email.lower(),
                                           account_type=account_type, profile_pic=validated_data['profile_pic'],
                                           gender=gender, phone=phone, country_code=country_code,
                                           formatted_phone=formatted_phone, dob=dob, bio=bio, create_profile=True,
                                           instagram_profile=instagram_profile)
                user.save()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
        return user

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


class CreateUserProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    profile_pic = serializers.FileField(validators=[image_validator], required=True)
    profile_thumbnail = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    phone = serializers.CharField(required=True)
    country_code = serializers.CharField(required=True)
    formatted_phone = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)
    social_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    instagram_profile = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone',
                  'dob', 'bio', 'email_verified', 'phone_verified', 'instagram_profile']

    def validate(self, attrs):
        dob = attrs.get("dob")
        instagram_profile = attrs.get("instagram_profile")
        if User.objects.filter(id=self.context['instance'].id, create_profile=True).exists():
            raise serializers.ValidationError({'error': _('profile already created')})
        if dob:
            age = relativedelta(date.today(), dob).years
            if age < 16:
                raise serializers.ValidationError(
                    {'dob': _("You must be 16 or older to use Sean App")})
        if User.objects.filter(phone=attrs.get("phone")).exists():
            raise serializers.ValidationError(
                {'phone': _("Phone number already exists")})
        if instagram_profile:
            if not instagram_profile.startswith(('https://www.instagram.com', 'www.instagram.com', 'instagram.com')):
                raise serializers.ValidationError(
                    {'instagram_profile': _("please enter a valid instagram profile url!")})
        return attrs

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


class SocialUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio', 'email_verified',
                  'phone_verified', 'instagram_profile']


class SocialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio', 'email_verified',
                  'phone_verified', 'instagram_profile']


class SigninSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    # username = serializers.CharField(required=False)
    password = serializers.CharField(
        max_length=128,
        label='Password',
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )
    device_id = serializers.CharField(required=True, write_only=True, allow_null=True, allow_blank=True)
    profile_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio',
                  'email_verified', 'phone_verified', 'password', 'device_id', 'instagram_profile']

    def validate(self, attrs):
        email = attrs.get('email')
        # username = attrs.get('username')
        password = attrs.get('password')
        device_id = attrs.get('device_id')
        if User.objects.filter(username=email.lower()).exists():
            user_email = User.objects.filter(username=email.lower()).first().email
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

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


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
            if User.objects.filter(email=email.lower(), account_type="Instagram").exists() \
                    or User.objects.filter(email=email.lower(), account_type="Apple").exists():
                raise serializers.ValidationError(
                    {'error': _('You can not reset password because you are Social User')})
        if phone:
            if not User.objects.filter(phone=phone).exists():
                raise serializers.ValidationError({'error': _('Phone does not exist')})
            if User.objects.filter(phone=phone, account_type="Instagram").exists() \
                    or User.objects.filter(phone=phone, account_type="Apple").exists():
                raise serializers.ValidationError(
                    {'error': _('You can not reset password because you are Social User')})
        return attrs


OTP_TYPE_CHOICES = (
    ('Email', 'Email'),
    ('Phone', 'Phone'),
)


class VerifyOtpSerializer(serializers.Serializer):
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)
    otp = serializers.CharField(required=True)
    otp_type = serializers.ChoiceField(choices=OTP_TYPE_CHOICES, required=True)


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

    @staticmethod
    def validate_password(data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError({'error': _('Password and confirm password does not match!')})
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    # phone = serializers.CharField(required=False)
    # country_code = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    bio = serializers.CharField(required=True)
    profile_pic = serializers.FileField(required=False)
    profile_thumbnail = serializers.SerializerMethodField()
    social_id = serializers.CharField(required=True)
    instagram_profile = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'social_id', 'account_type', 'create_profile', 'is_account',
                  'profile_pic', 'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone',
                  'dob', 'bio', 'email_verified', 'phone_verified', 'instagram_profile']

    def validate(self, attrs):
        # phone = attrs.get('phone')
        dob = attrs.get('dob')
        instagram_profile = attrs.get('instagram_profile')
        profile_pic = attrs.get('profile_pic')
        if dob:
            age = relativedelta(date.today(), dob).years
            if age < 16:
                raise serializers.ValidationError(
                    {'dob': _("You must be 16 or older to use Sean App")})
        user = self.context['request'].user
        # if User.objects.filter(phone=phone, create_profile=True).exclude(id=user.id).exists():
        #     raise serializers.ValidationError({'phone': _('phone already exists')})
        profile = User.objects.filter(id=user.id).first().profile_pic
        user_profile_img = profile.name.split("profile_photos/")[1]
        if profile_pic:
            if not profile_pic.name == user_profile_img:
                # profile_thumbnail = attrs.get('profile_thumbnail')
                delete_image(user_profile_img)

        # if attrs.get('profile_thumbnail'):
        #     profile_thumbnail = attrs.get('profile_thumbnail')
        #     profile_thumb = User.objects.filter(id=user.id).first().profile_thumbnail

        # profile_thumb_data = profile_thumb.name.split("profile_thumbnails/")[1]
        # if profile_data == False and profile_thumb_data == False:
        #     delete_image(profile=profile, profile_thumb=profile_thumb)
        if instagram_profile:
            if not instagram_profile.startswith(('https://www.instagram.com', 'www.instagram.com', 'instagram.com')):
                raise serializers.ValidationError(
                    {'instagram_profile': _("please enter a valid instagram profile url!")})
        return attrs

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


class BlockUserSerializer(serializers.ModelSerializer):
    block_user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)

    class Meta:
        model = BlockUser
        fields = ['block_user']

    def validate(self, attrs):
        user = self.context['request'].user
        blocked_user = attrs['block_user']

        if user == blocked_user:
            message = "You can not block yourself"
            raise serializers.ValidationError(_(message))
        if BlockUser.objects.filter(block_user=blocked_user):
            message = "User already been blocked"
            raise serializers.ValidationError(_(message))
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['block_user'] = UserSerializer(instance.block_user).data
        return data


class UnblockUserSerializer(serializers.ModelSerializer):
    block_user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='id', required=True)

    class Meta:
        model = BlockUser
        fields = ['block_user']

    def validate(self, attrs):
        user = self.context['request'].user
        blocked_user = attrs['block_user']

        if user == blocked_user:
            message = "You can not unblock yourself"
            raise serializers.ValidationError(_(message))
        if not BlockUser.objects.filter(block_user=blocked_user):
            message = "User already been unblocked"
            raise serializers.ValidationError(_(message))
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['block_user'] = UserSerializer(instance.block_user).data
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    profile_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'create_profile', 'social_id', 'is_account', 'profile_pic',
                  'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio',
                  'email_verified', 'phone_verified', 'account_type', 'instagram_profile']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user_friend = Friend.objects.filter(user=instance).values_list("friend_id", flat=True)
        friend_user = Friend.objects.filter(friend=instance).values_list("user_id", flat=True)
        friends_list = list(user_friend) + (list(friend_user))
        data['friend_list'] = friends_list
        return data

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


class UserProfileStatusSerializer(serializers.ModelSerializer):
    is_account = serializers.ChoiceField(choices=ACCOUNT_CHOICE, required=True)

    class Meta:
        model = User
        fields = ['is_account']


class UsersProfileSerializer(serializers.ModelSerializer):
    # is_friend = serializers.SerializerMethodField()
    profile_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'create_profile', 'social_id', 'is_account', 'profile_pic',
                  'profile_thumbnail', 'gender', 'country_code', 'formatted_phone', 'phone', 'dob', 'bio',
                  'email_verified', 'phone_verified', 'account_type', 'instagram_profile']

    # def get_is_friend(self, obj):
    #     if Friend.objects.filter(Q(user=obj) | Q(friend=obj)).exists():
    #         return True
    #     else:
    #         return False

    def get_profile_thumbnail(self, obj):
        return get_thumb(obj)


class SocialProfileExistSerializer(serializers.Serializer):
    social_id = serializers.CharField(required=True)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    # def validate(self, attrs):
    #     email = attrs.get('email')
    #     username = attrs.get('username')
    #     if email is None and username is None:
    #         raise serializers.ValidationError({'error': _('Email or username is required, Please enter one of them')})
    #     return attrs
