from rest_framework import exceptions


class PermissionsUtil:

    @staticmethod
    def permission(request, instance):
        if request.user.is_superuser or instance.user == request.user:
            return True
        raise exceptions.PermissionDenied()
