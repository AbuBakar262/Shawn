from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, BlockUser
from accounts.serializer.create_account_serializers import CreateUserProfileSerializer
from accounts.serializer.signin_serializers import UserSerializer


class CreateUserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserProfileSerializer
    permission_classes = [AllowAny]

    def create_profile(self, request, *args, **kwargs):
        try:
            # get email from request and update email user object
            email = request.data.get('email')
            user = User.objects.get(email=email)
            user_serializer = CreateUserProfileSerializer(user, data=request.data)
            if user_serializer.is_valid():
                user_serializer.save(create_profile=True)
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_201_CREATED,
                    "message": "User profile created successfully",
                    "responsePayload": user_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": user_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)