import random
import string
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings


def random_string_generator():
    chars = string.digits
    size = 6
    return ''.join(random.choice(chars) for x in range(size))


def send_otp_via_email(email):
    subject = 'OTP for email verification'
    otp = random_string_generator()
    message = f'Your verification code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return otp

