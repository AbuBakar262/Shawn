import random
import string
from django.utils.translation import gettext_lazy as _
import boto3
from twilio.rest import Client
from rest_framework import serializers
from accounts.models import User
from notification.models import DeviceRegistration
from sean_backend.settings import ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, \
    AWS_STORAGE_BUCKET_NAME


def random_string_generator():
    chars = string.digits
    size = 6
    return ''.join(random.choice(chars) for x in range(size))


def send_otp_phone(to):
    try:
        '''Use the Twilio API to send the phone number a text message containing an OTP'''
        client = Client(ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO)
        verify = client.verify.services('VA633cf1dff0855edb1bef9d17fceccffc')
        msg_sent = verify.verifications.create(to=to, channel='sms')
        e = "sent"
        return e
    except Exception as e:
        return e.msg


def verify_otp_phone(to, code):
    try:
        ''' Verify the OTP code with the phone number'''
        client = Client(ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO)
        verify = client.verify.services('VA633cf1dff0855edb1bef9d17fceccffc')
        result = verify.verification_checks.create(to=to, code=code)
        if result.status == 'approved':
            e = "approved"
            return e
    except Exception as e:
        return e.msg


def send_otp_email(to):
    try:
        client = Client(ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO)
        verify = client.verify.services('VA633cf1dff0855edb1bef9d17fceccffc')
        msg_sent = verify.verifications.create(to=to, channel='email')
        e = "sent"
        return e
    except Exception as e:
        return e.msg


def verify_otp_email(to, code):
    try:
        client = Client(ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO)
        verify = client.verify.services('VA633cf1dff0855edb1bef9d17fceccffc')
        result = verify.verification_checks.create(to=to, code=code)
        if result.status == 'approved':
            e = "approved"
            return e
    except Exception as e:
        return e.msg


def delete_image(profile, profile_thumb):
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = AWS_STORAGE_BUCKET_NAME
    key = profile.name
    key_thumb = profile_thumb.name
    if profile:
        client.delete_object(Bucket=bucket, Key=key)
    if profile_thumb:
        client.delete_object(Bucket=bucket, Key=key_thumb)
        return True
    else:
        return False


# When user Login device_id will be saved in DeviceRegistration table
def social_login(username, social_id, device_id):

    if not User.objects.filter(username=username).exists():
        raise serializers.ValidationError({'username': _('username does not exists')})

    if User.objects.filter(social_id=social_id, username=username).exists():
        user = User.objects.filter(social_id=social_id, username=username).first()
        if not DeviceRegistration.objects.filter(user=user).exists():
            DeviceRegistration.objects.create(user=user, registration_id=device_id)
        if not DeviceRegistration.objects.filter(user=user, registration_id=device_id).exists():
            DeviceRegistration.objects.filter(user=user).update(registration_id=device_id)
        return user
    else:
        raise serializers.ValidationError({'unauthorized': _('Invalid credentials')})
