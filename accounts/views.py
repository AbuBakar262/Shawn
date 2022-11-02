from accounts.models import User
from accounts.serializers import (SignupSerializer, UserSerializer,
                                  CreateUserProfileSerializer, SigninSerializer,
                                  ForgotPasswordSerializer, ChangePasswordSerializer)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from accounts.utils import send_otp_via_email


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

    def forgot_password(self, request, *args, **kwargs):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            link = "http://localhost:3000/accounts/api/forgot_change_password/" + urlsafe_base64_encode(
                force_bytes(user.pk)) + "/" + PasswordResetTokenGenerator().make_token(user) + "/"
            send_otp_via_email(request.data.get('email'), link)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Reset password link sent to your email",
                        "responsePayload": serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def forgot_change_password(self, request, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(kwargs['uidb64']).decode()
            if not User.objects.filter(pk=uid).exists():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(pk=uid)
            if not PasswordResetTokenGenerator().check_token(user, kwargs['token']):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid token"
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = ChangePasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if user.check_password(request.data.get('password')):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Your new password must be different from the old password",
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('password'))
            user.save()
            user_serializer = UserSerializer(user)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Password changed successfully",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
