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

from sean_backend.utils import PermissionsUtil


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
            response = {"statusCode": 201, "error": False, "message": "User created successfully!",
                        "data": serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CreateUserProfileSerializer(instance, data=request.data, partial=partial,
                                                 context={'instance': instance})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "message": "Profile Created Successfully!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save(create_profile=True)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


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
            user_data = serializer.data
            user = User.objects.get(email=user_data.get("email"))
            if not user_data.get('create_profile'):
                return Response(data={
                    "statusCode": 201,
                    "error": False,
                    "message": "User logged in successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                data={
                    "statusCode": 201,
                    "error": False,
                    "message": "User logged in successfully",
                    "data": {
                        "user": serializer.data,
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
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "OTP sent to phone number successfully",
                    "data": {
                        "user": user_serializer.data,
                    }
                }, status=status.HTTP_200_OK)
            else:
                user = User.objects.filter(email=email).first()
                send_otp_email(user.email)
                user_serializer = UserSerializer(user)
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "OTP sent to Email successfully",
                    "data": {
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
                    "statusCode": 400, "error": False,
                    "message": "Invalid OTP",
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
            user_serializer = UserSerializer(user)
            return Response(data={
                "statusCode": 200, "error": False,
                "message": "OTP verified successfully please reset your password!",
                "data": {
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
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response('Password changed successfully', UserSerializer),
            400: openapi.Response('Bad request', UserSerializer),
        }
    )
    def reset_password(self, request, *args, **kwargs):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
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
                "statusCode": 200, "error": False,
                "message": "Reset Password Successfully",
                "data": {
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
            if User.objects.filter(id=user.id).exists():
                profile = User.objects.filter(id=user.id).first()
                serializer_ = UserProfileSerializer(profile)
                user_serializer = serializer_.data
            else:
                response = {"statusCode": 200, "error": False,
                            "message": "User profile matching query does not exist!",
                            "data": {
                            }}
                return Response(data=response, status=status.HTTP_200_OK)
            user_event_serializer = EventListSerializer(Event.objects.filter(user=user), many=True)
            user_location_serializer = UserLocationSerializer(UserLocation.objects.filter(user=user), many=True)
            response = {"statusCode": 200, "error": False,
                        "message": "User profile details",
                        "data": {
                            "user": user_serializer,
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
        if self.action in ['edit_profile'] or self.action in ['delete_profile'] or self.action in [
            'profile_status'] or self.action in ['profile']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class SocialViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Social Signup",
        request_body=SocialSignupSerializer
    )
    def social_signup(self, request, *args, **kwargs):
        try:
            serializer = SocialSignupSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            data = serializer.data
            if data.get("create_profile"):
                result = {
                    "user": serializer.data,
                    "access": str(AccessToken.for_user(serializer.instance)),
                    "refresh": str(RefreshToken.for_user(serializer.instance)),
                }
                return Response(data={
                    "statusCode": 201, "error": False,
                    "message": "User signup successfully",
                    "data": result
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(data={
                    "statusCode": 201, "error": False,
                    "message": "User signup successfully",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e)}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Social Login",
        request_body=SocialSignupSerializer
    )
    def social_login(self, request, *args, **kwargs):
        try:
            serializer = SocialLoginSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer_data = serializer.data
            if serializer_data.get("create_profile"):
                user = User.objects.filter(id=serializer_data.get("id")).first()
                result = {
                    "user": serializer_data,
                    "access": str(AccessToken.for_user(user)),
                    "refresh": str(RefreshToken.for_user(user)),
                }
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "User Login successfully",
                    "data": result
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "User Login successfully",
                    "data": serializer_data
                }, status=status.HTTP_200_OK)
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
