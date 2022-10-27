from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User
from accounts.serializer.signin_serializers import SigninSerializer


class SigninModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SigninSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = SigninSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            if not user.is_verified:
                return Response(data={"message": "Please verify your email"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                data={
                    "message": "User logged in successfully",
                    "responsePayload": {
                        "refresh": str(RefreshToken.for_user(user)),
                        "access": str(AccessToken.for_user(user)),
                        "user": serializer.data
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(data={"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
