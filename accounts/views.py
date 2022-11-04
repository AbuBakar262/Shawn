from accounts.models import User
from accounts.serializers import (SignupSerializer, UserSerializer,
                                  CreateUserProfileSerializer, SigninSerializer,
                                  ForgotPasswordSerializer, ChangePasswordSerializer,
                                  UserProfileUpdateSerializer, SocialSerializer,
                                  SocialCreateUserProfileSerializer)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from accounts.utils import send_otp_via_email
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Signup",
        request_body=SignupSerializer
    )
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
                "result": serializer.data['user']
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Create user profile",
        request_body=CreateUserProfileSerializer,
        responses={
            201: openapi.Response('User profile created successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
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
                    "result": user_serializer.data
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

    @swagger_auto_schema(
        operation_description="Signin",
        request_body=SigninSerializer,
        responses={
            200: openapi.Response('User logged in successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
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
                    "result": user_serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User logged in successfully",
                    "result": {
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

    @swagger_auto_schema(
        operation_description="Forgot password",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response('OTP sent to email successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
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

    @swagger_auto_schema(
        operation_description="Reset Password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response('Password changed successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
    def reset_password(self, request, *args, **kwargs):
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


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated]

    def profile_details(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.data.get('id'))
            if not user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            user_serializer = UserSerializer(user)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile details",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Profile Edit",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: openapi.Response('Profile updated successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
    def profile_edit(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserProfileUpdateSerializer(user, data=request.data)
            if not serializer.is_valid():
                return Response(
                    data={
                        "status": "error",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save()
            user_serializer = UserSerializer(user)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile updated successfully",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def profile_list(self, request, *args, **kwargs):
        try:
            user = User.objects.exclude(is_superuser=True)
            user_serializer = UserSerializer(user, many=True)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile list",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


    def profile_status(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.is_account = request.data.get('is_account')
            user.save()
            user_serializer = UserSerializer(user)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile status changed successfully",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def profile_delete(self, request, *args, **kwargs):
        try:
            user = request.user
            user.delete()
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile deleted successfully"}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in ['profile_edit', 'profile_delete', 'profile_status']:
            permission_classes = [IsAuthenticated]
        if self.action in ['profile_details', 'profile_list']:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class SocialViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Social Signup",
        request_body=SocialSerializer
    )
    def social_login(self, request, *args, **kwargs):
        try:
            serializer = SocialSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            data = serializer.data
            if data.get("create_profile") == True:
                result = {
                    "user": serializer.data,
                    "access": str(AccessToken.for_user(serializer.instance)),
                    "refresh": str(RefreshToken.for_user(serializer.instance)),
                }
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User signup successfully",
                    "responsePayload": result
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User signup successfully",
                    "responsePayload": serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Social Profile Create",
        request_body=SocialCreateUserProfileSerializer
    )
    def social_profile_create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = User.objects.get(email=email)
            serializer = SocialCreateUserProfileSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save(create_profile=True)
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User profile created successfully",
                    "responsePayload": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)