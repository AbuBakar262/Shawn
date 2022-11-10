from friends_management.models import Friend
from accounts.serializers import *
from location.serializers import *
from event.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.utils import *
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
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
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
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
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
                        "access": str(AccessToken.for_user(user)),
                        "refresh": str(RefreshToken.for_user(user))
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
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            phone = request.data.get('phone')
            email = request.data.get('email')
            if phone:
                user = User.objects.filter(phone=phone).first()
                send_otp_phone(user.phone)
                user_serializer = UserSerializer(user)
            else:
                user = User.objects.filter(email=email).first()
                send_otp_email(email)
                user_serializer = UserSerializer(user)
            return Response(data={
                "status": "success","status_code": status.HTTP_200_OK,
                "message": "OTP sent to phone number successfully",
                "result": {
                    "user": user_serializer.data,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"status": "error", "status_code": status.HTTP_400_BAD_REQUEST, "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def verify_otp(self, request, *args, **kwargs):
        try:
            serializer = VerifyOtpSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            otp = serializer.validated_data.get('otp')
            user = User.objects.get(id=request.data.get('user'))
            phone_otp = verify_otp_phone(user.phone, otp)
            if phone_otp != 'approved':
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid OTP"
                }, status=status.HTTP_400_BAD_REQUEST)
            user_serializer = UserSerializer(user)
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "OTP verified successfully please reset your password!",
                "result": {
                    "user": user_serializer.data,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

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
            serializer = ChangePasswordSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(id=self.request.data.get('user'))
            if user.check_password(request.data.get('password')):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "New password cannot be same as old password!"
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data.get('password'))
            user.save()
            user_serializer = UserSerializer(user)
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Password changed successfully",
                "result": {
                    "user": user_serializer.data,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated]

    def profile(self, request, *args, **kwargs):
        try:
            user = request.user
            user_serializer = UserSerializer(user)
            user_event_serializer = EventListSerializer(Event.objects.filter(user=user), many=True)
            user_location_serializer = UserLocationSerializer(UserLocation.objects.filter(user=user), many=True)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "User profile details",
                        "result": {
                            "user": user_serializer.data,
                            "location": user_location_serializer.data,
                            "map": user_event_serializer.data,
                        }}
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
    def edit_profile(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserProfileUpdateSerializer(user, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
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

    def delete_profile(self, request, *args, **kwargs):
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
        if self.action in ['edit_profile'] or self.action in ['delete_profile'] or self.action in ['profile_status'] or self.action in ['profile']:
            permission_classes = [IsAuthenticated]
        else:
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
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
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


class BlockUserViewSet(viewsets.ModelViewSet):
    queryset = BlockUser.objects.all()
    serializer_class = BlockUserSerializer
    permission_classes = [IsAuthenticated]


    def block_user(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user = User.objects.get(id=request.data.get('blocked_user'))
            if not blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            if user == blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You can not block yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            if user in BlockUser.objects.filter(block_user=blocked_user):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User already blocked"
                }, status=status.HTTP_400_BAD_REQUEST)
            if Friend.objects.filter(user=request.user, friend=blocked_user).exists():
                user_friend = Friend.objects.filter(user=request.user, friend=blocked_user).first()
                user_friend.delete()
            block_user = BlockUser.objects.create(block_user=blocked_user, user=user)
            serializer = BlockUserSerializer(block_user)
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "User blocked successfully",
                "result": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def blocked_user_list(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user = BlockUser.objects.filter(user=user)
            serializer = BlockUserSerializer(blocked_user, many=True)
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Blocked user list",
                "result": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    def unblock_user(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user = User.objects.get(id=request.data.get('blocked_user'))
            if not blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            if user == blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You can not unblock yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            if not BlockUser.objects.filter(block_user=blocked_user).exists():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User is not blocked"
                }, status=status.HTTP_400_BAD_REQUEST)
            block_user = BlockUser.objects.filter(block_user=blocked_user).first()
            block_user.delete()
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "User unblocked successfully",
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)