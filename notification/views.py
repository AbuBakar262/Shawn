from friends_management.serializers import FriendRequestListSerializer
from notification.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Case, When, Value, IntegerField
# Create your views here.


class DeviceRegistrationViewSet(viewsets.ModelViewSet):
    queryset = DeviceRegistration.objects.all()
    serializer_class = DeviceRegistrationSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = DeviceRegistrationSerializer(queryset, many=True)
            response = {"statusCode": 200, "error": False, "data": serializer.data, "message": "Device List"}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = DeviceRegistration.objects.all()
    serializer_class = DeviceRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            if Notification.objects.filter(receiver=user, read_status=False).exists():
                Notification.objects.filter(receiver=user, read_status=False).update(read_status=True)
            friend_request = Notification.objects.filter(receiver=user).annotate(
                type_order=Case(
                    When(type='Send Request',
                         then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('type_order', '-created_at')
            serializer = FriendRequestListSerializer(friend_request, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Notification List",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def total_notifications(self, request, *args, **kwargs):
        try:
            user = request.user
            if Notification.objects.filter(receiver=user, read_status=False).exists():
                notifications = Notification.objects.filter(receiver=user, read_status=False).count()
            else:
                notifications = 0
            response = {"statusCode": 200, "error": False, "message": "Total Notifications!",
                        "data": notifications}
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def notification_active(self, request, *args, **kwargs):
        serializer = NotificationActiveSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        active = request.data.get("active")
        if SeanSetting.objects.filter(user=request.user).exists():
            SeanSetting.objects.filter(user=request.user).update(notification_status=active)
        else:
            sean = SeanSetting.objects.create(user=request.user, notification_status=active)
            sean.save()
        data = {
            "notification_active": active
        }
        response = {"statusCode": 20, "error": False, "message": "Notification Status Updated Successfully!",
                    "data": data}
        return Response(response, status=status.HTTP_201_CREATED)
