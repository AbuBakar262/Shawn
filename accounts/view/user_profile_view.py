from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User
from accounts.serializer.signin_serializers import SigninSerializer
from accounts.serializer.signin_serializers import UserSerializer


class ProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def profile_details(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get('email'))
            if request.user.is_superuser:
                user_serializer = UserSerializer(user)
                return Response(
                    data={
                        "message": "User data fetched successfully",
                        "responsePayload": user_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            if request.user == user:
                user_serializer = UserSerializer(user)
                return Response(
                    data={
                        "message": "User data fetched successfully",
                        "responsePayload": user_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "You are not authorized to view this user data"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
