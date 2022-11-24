from rest_framework import exceptions, status
from pyfcm import FCMNotification
from rest_framework.response import Response

from sean_backend.settings import FIREBASE_API_KEY
push_service = FCMNotification(api_key=FIREBASE_API_KEY)

class PermissionsUtil:

    @staticmethod
    def permission(request, instance):
        if request.user.is_superuser or instance.user == request.user:
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
