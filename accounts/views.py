from accounts.models import User
from accounts.serializers import SignupSerializer, UserSerializer, CreateUserProfileSerializer, SigninSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def signup(self, request, *args, **kwargs):
        try:
            serializer = SignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "message": "User created successfully",
                "responsePayload": serializer.data['user']
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def create_profile(self, request, *args, **kwargs):
        try:
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

    def login(self, request, *args, **kwargs):
        try:
            serializer = SigninSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            user_serializer = UserSerializer(user)
            if not user.create_profile:
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User logged in successfully",
                    "responsePayload": user_serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
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
