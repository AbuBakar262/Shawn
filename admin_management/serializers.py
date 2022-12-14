from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from accounts.models import *
from admin_management.models import ReportUser


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


class CreateReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = ['reported_by', 'reported_to', 'reason']

    def validate(self, attrs):
        reported_by = attrs.get('reported_by')
        reported_to = attrs.get('reported_to')
        if reported_by == reported_to:
            raise serializers.ValidationError({'error': _('You cannot report yourself')})
        if ReportUser.objects.filter(reported_by=reported_by, reported_to=reported_to).exists():
            raise serializers.ValidationError({'error': _('You have already reported this user')})
        return attrs


class ListReportUserSerializer(serializers.ModelSerializer):
    reported_by = serializers.SerializerMethodField()
    reported_to = serializers.SerializerMethodField()

    class Meta:
        model = ReportUser
        fields = ['reported_by', 'reported_to', 'reason', 'created_at', 'updated_at']

    def get_reported_by(self, obj):
        return obj.reported_by.email

    def get_reported_to(self, obj):
        return obj.reported_to.email


class UpdateReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUser
        fields = ['reason']

    def validate(self, attrs):
        reason = attrs.get('reason')
        if not reason:
            raise serializers.ValidationError({'error': _('Reason cannot be empty')})
        return attrs
