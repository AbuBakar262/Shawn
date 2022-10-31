from rest_framework import serializers
from accounts.models import *
from django.utils.translation import gettext_lazy as _

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)


class SignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, label='Password', style={'input_type': 'password'},
                                     write_only=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    contact = serializers.CharField(max_length=50, required=False)
    instagram = serializers.CharField(max_length=100, required=False)
    dob = serializers.DateField(label='Date of Birth', required=False)
    bio = serializers.CharField(label='Additional Information', required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password',
                  'gender', 'contact', 'instagram', 'dob', 'bio']

    def validate(self, attrs):
        # if not attrs.get('first_name').isalpha():
        #     raise serializers.ValidationError(_('First Name must be alphabetical'))
        # if not attrs.get('last_name').isalpha():
        #     raise serializers.ValidationError(_('Last Name must be alphabetical'))
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        # if attrs['password'] != attrs['confirm_password']:
        #     raise serializers.ValidationError({'password': 'Password does not match'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


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