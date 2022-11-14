import random
import string
from twilio.rest import Client
from sean_backend.settings import ACCOUNT_SID_TWILIO, AUTH_TOKEN_TWILIO


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
