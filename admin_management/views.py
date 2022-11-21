from accounts.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from admin_management.serializers import AdminLoginSerializer


class AdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def login(self, request, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        user_data = UserSerializer(user).data
        response = {"statusCode": 200, "error": False, "message": "Admin Login successfully!", "data": user_data}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.exclude(is_superuser=True)
            user_serializer = UserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "User List", "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
