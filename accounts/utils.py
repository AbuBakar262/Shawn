import random
import string

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
import boto3
from twilio.rest import Client
from rest_framework import serializers
from accounts.models import User
from friends_management.models import Friend
from location.utils import get_mongodb_database
from notification.models import DeviceRegistration
from sean_backend.settings import ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, \
    AWS_STORAGE_BUCKET_NAME, THUMBNAIL_LINK


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


def delete_image(profile):
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    bucket = AWS_STORAGE_BUCKET_NAME
    key = profile
    if profile:
        client.delete_object(Bucket=bucket, Key=key)
        return True
    else:
        return False


# When user Login device_id will be saved in DeviceRegistration table
def social_login(username, social_id, device_id, email):
    if username:
        # if not User.objects.filter(username=username.lower()).exists():
        #     raise serializers.ValidationError({'username': _('username does not exists')})

        if User.objects.filter(social_id=social_id, username=username.lower()).exists():
            user = User.objects.filter(social_id=social_id, username=username.lower()).first()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
            if not DeviceRegistration.objects.filter(user=user, registration_id=device_id).exists():
                DeviceRegistration.objects.filter(user=user).update(registration_id=device_id)
            return user
        else:
            raise serializers.ValidationError({'unauthorized': _('Invalid credentials')})
    else:
        # if not User.objects.filter(email=email.lower()).exists():
        #     raise serializers.ValidationError({'email': _('email does not exists')})

        if User.objects.filter(social_id=social_id, email=email.lower()).exists():
            user = User.objects.filter(social_id=social_id, email=email.lower()).first()
            if not DeviceRegistration.objects.filter(user=user).exists():
                DeviceRegistration.objects.create(user=user, registration_id=device_id)
            if not DeviceRegistration.objects.filter(user=user, registration_id=device_id).exists():
                DeviceRegistration.objects.filter(user=user).update(registration_id=device_id)
            return user
        else:
            raise serializers.ValidationError({'unauthorized': _('Invalid credentials')})

def social_account_exist(username, social_id, email):
    if username:
        if User.objects.filter(social_id=social_id, username=username.lower()).exists():
            return True
        else:
            return False
    else:
        if email:
            if User.objects.filter(social_id=social_id, email=email.lower(), account_type='Apple').exists():
                return True
            else:
                return False
        else:
            if User.objects.filter(social_id=social_id, account_type='Apple').exists():
                return True
            else:
                return False


def get_thumb(obj):
    if User.objects.filter(id=obj.id).exists():
        profile = User.objects.filter(id=obj.id).first().profile_pic.name
        if profile:
            return THUMBNAIL_LINK + profile
        else:
            return None
    else:
        return None


def user_remove_mongo(user):
    try:
        Friend.objects.filter(Q(user=user) | Q(friend=user)).delete()
        dbname = get_mongodb_database()
        collection_name = dbname["SeanCollection"]
        collection_name.delete_one({"user_id": user.id})
        user_found_in_friend_list = collection_name.find({"friends_list": user.id})
        for i in user_found_in_friend_list:
            if user.id in i.get("friends_list"):
                i.get("friends_list").remove(user.id)
                friends_list = i.get("friends_list")
                values = {"$set": {"friends_list": friends_list}}
                # update_friend_list = collection_name.find({"user_id": i.get("user_id")})
                # myquery = update_friend_list[0]
                collection_name.update_one(i, values)
        return True
    except Exception as e:
        return e.args[0]
