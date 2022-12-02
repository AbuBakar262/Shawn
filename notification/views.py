from friends_management.serializers import FriendRequestListSerializer
from notification.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


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
            friend_request = Notification.objects.filter(receiver=user)
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
