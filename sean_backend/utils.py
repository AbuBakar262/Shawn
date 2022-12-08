import json

import requests
from rest_framework import exceptions, status
from pyfcm import FCMNotification
from rest_framework.response import Response
from google.oauth2 import service_account
import google.auth.transport.requests
from sean_backend.settings import FIREBASE_API_KEY, FIREBASE_URL, FIREBASE_SCOPES

push_service = FCMNotification(api_key=FIREBASE_API_KEY)


class PermissionsUtil:

    @staticmethod
    def permission(request, instance):
        if request.user.is_superuser or instance.user == request.user:
            return True
        raise exceptions.PermissionDenied()

    @staticmethod
    def current_user_permission(request, instance):
        if request.user.is_superuser or instance == request.user:
            return True
        raise exceptions.PermissionDenied()

    @staticmethod
    def destroy_permission(request, instance):
        if request.user.is_superuser or instance == request.user:
            return True
        raise exceptions.PermissionDenied()


def notification(device_id, title, body):
    push_service.notify_single_device(registration_id=device_id, message_title=title,
                                                      message_body=body)


def firebase_notification(device_id, title, body):
    SCOPES = [FIREBASE_SCOPES]
    credentials = service_account.Credentials.from_service_account_file(
        'firebase_account_file/sean-f9f51-firebase-adminsdk-gwhhn-45381e805f.json', scopes=SCOPES)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    access_token = credentials.token
    url = FIREBASE_URL
    payload = json.dumps({
        "message": {
            "token": device_id,
            "data": {
                "title": title,
                "body": body
            }
        }
    })
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    if not response['error']['code'] == 200:
        return False
    else:
        return True
