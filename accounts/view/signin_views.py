from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User
from accounts.serializer.signin_serializers import SigninSerializer
from accounts.serializer.signin_serializers import UserSerializer


class SigninViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SigninSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = SigninSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "responsePayload": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            user_serializer = UserSerializer(user)
            if not user.create_profile:
                return Response(data={
                    "status": "error",
                    "status_code": 400,
                    "message": "User logged in successfully",
                    "responsePayload": user_serializer.data
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                data={
                    "message": "User logged in successfully",
                    "responsePayload": {
                        "user": user_serializer.data,
                        "refresh": str(RefreshToken.for_user(user)),
                        "access": str(AccessToken.for_user(user))
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
