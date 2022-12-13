from rest_framework.views import APIView

from friends_management.models import Friend
from accounts.serializers import *
from location.serializers import *
from event.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.utils import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from location.utils import get_mongodb_database
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
            response = {"statusCode": 201, "error": False, "message": "User Registered Successfully!",
                        "data": serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user_id = kwargs.get('pk')
        if not User.objects.filter(id=user_id).exists():
            error = "User not found"
            return Response(data={
                "statusCode": 404, "error": True,
                "message": "User not found",
                "errors": {"error": [error]}
            }, status=status.HTTP_404_NOT_FOUND)
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
                    "data": {
                        "create_profile": serializer.data.get("create_profile"),
                        "user": serializer.data,
                        "access": str(AccessToken.for_user(instance)),
                        "refresh": str(RefreshToken.for_user(instance))}}
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
                    "statusCode": 200,
                    "error": False,
                    "message": "User logged in successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(
                data={
                    "statusCode": 200,
                    "error": False,
                    "message": "User logged in successfully",
                    "data": {
                        "create_profile": serializer.data.get("create_profile"),
                        "user": serializer.data,
                        "access": str(AccessToken.for_user(user)),
                        "refresh": str(RefreshToken.for_user(user))
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
                if not user.formatted_phone:
                    return Response(data={
                        "statusCode": 400, "error": True,
                        "message": "phone does not exist",
                        "errors": {"error": ["phone does not exist!"]}
                    }, status=status.HTTP_400_BAD_REQUEST)
                otp = send_otp_phone(user.formatted_phone + user.phone)
                if otp != 'sent':
                    return Response(data={
                        "statusCode": 400, "error": True,
                        "message": otp,
                        "errors": {"error": ["Phone OTP not sent!"]}
                    }, status=status.HTTP_400_BAD_REQUEST)
                user_serializer = UserSerializer(user)
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "OTP sent to phone number successfully",
                    "data": {
                        "user": user_serializer.data,
                    }
                }, status=status.HTTP_200_OK)
            else:
                user = User.objects.filter(email=email.lower()).first()
                otp = send_otp_email(user.email)
                if otp != 'sent':
                    return Response(data={
                        "statusCode": 400, "error": True,
                        "message": otp,
                        "errors": {"error": ["Email OTP not sent!"]}
                    }, status=status.HTTP_400_BAD_REQUEST)
                user_serializer = UserSerializer(user)
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "OTP sent to Email successfully",
                    "data": {
                        "user": user_serializer.data,
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
            otp_type = request.data.get('otp_type')
            if otp_type == 'Phone':
                phone_otp = verify_otp_phone(user.phone, otp)
                if phone_otp != 'approved':
                    return Response(data={
                        "statusCode": 400, "error": True,
                        "message": phone_otp,
                        "errors": {"error": ["phone otp is not verified!"]}
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                email_otp = verify_otp_email(user.email, otp)
                if email_otp != 'approved':
                    return Response(data={
                        "statusCode": 400, "error": True,
                        "message": email_otp,
                        "errors": {"error": ["email otp is not verified!"]}
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
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    # permission_classes = [AllowAny]

    def user_profile(self, request, *args, **kwargs):
        try:
            user = request.user
            user_id = self.request.query_params.get('id')
            if user_id:
                if not User.objects.filter(id=user_id).exists():
                    response = {"statusCode": 404, "error": False,
                                "message": "User not found!",
                                "data": {
                                    "error": ["User not found!"]
                                }}
                    return Response(data=response, status=status.HTTP_404_NOT_FOUND)
                user_serializer = UsersProfileSerializer(User.objects.get(id=user_id), context={"user_id": user_id})
                data = user_serializer.data
                friend = User.objects.filter(id=user_id).first()
                if Friend.objects.filter(Q(user=request.user, friend=friend) | Q(friend=request.user, user=friend)).exists():
                    data['is_friend'] = True
                else:
                    data['is_friend'] = False
                dbname = get_mongodb_database()
                collection_name = dbname["SeanCollection"]
                user_location = collection_name.find({"user_id": int(user_id)}, {'_id': 0})
                for i in user_location:
                    if i.get("location"):
                        data['latitude'] = i.get("location").get("coordinates")[1]
                        data['longitude'] = i.get("location").get("coordinates")[0]
                    else:
                        data['latitude'] = 0.00
                        data['longitude'] = 0.00
                response = {"statusCode": 200, "error": False,
                            "message": "User profile fetched successfully",
                            "data": {
                                "user": data,
                            }}
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                profile = User.objects.filter(id=user.id).first()
                serializer_ = UserProfileSerializer(profile)
                user_serializer = serializer_.data
                user_event_serializer = EventListSerializer(Event.objects.filter(user=user), many=True)
                user_location_serializer = UserLocationSerializer(FavouriteLocation.objects.filter(user=user), many=True)
                response = {"statusCode": 200, "error": False,
                            "message": "User profile details",
                            "data": {
                                "user": user_serializer,
                                "location": user_location_serializer.data,
                                "map": user_event_serializer.data,
                            }}
                return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.current_user_permission(request, instance)
        serializer = UserProfileUpdateSerializer(instance, data=request.data, partial=partial,
                                                 context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "message": "Profile Updated Successfully!",
                    "data": {"user": serializer.data}}
        return Response(data=response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            user = User.objects.exclude(is_superuser=True).exclude(id=user.id).exclude(create_profile=False)
            user_serializer = UserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "User List", "data": user_serializer.data, "count": user.count()}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def profile_status(self, request, *args, **kwargs):
        try:
            serializer = UserProfileStatusSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            user.is_account = serializer.validated_data.get('is_account')
            user.save()
            user_serializer = UserSerializer(user)
            response = {"statusCode": 200, "error": False,
                        "message": "User profile status updated successfully",
                        "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.destroy_permission(request, instance)
        user_remove_mongo(instance)
        profile = User.objects.filter(id=instance.id).first().profile_pic
        delete_image(profile.name.split("/")[1])
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "message": "User profile deleted successfully!"}
        return Response(data=response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def get_permissions(self):
        if self.action in ['user_profile'] or self.action in \
                ['profile_status'] or self.action in ['profile'] or self.action in ['list'] or self.action in ['retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class SocialViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Social Login",
        request_body=SocialLoginSerializer
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
            serializer_data = serializer.save()
            serializer_detail = SocialLoginSerializer(serializer_data)
            user = User.objects.filter(id=serializer_detail.data.get('id')).first()
            result = {
                "create_profile": serializer_detail.data.get("create_profile"),
                "user": serializer_detail.data,
                "access": str(AccessToken.for_user(user)),
                "refresh": str(RefreshToken.for_user(user)),
            }
            return Response(data={
                "statusCode": 200, "error": False,
                "message": "User Login successfully",
                "data": result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def social_profile_exist(self, request, *args, **kwargs):
        try:
            serializer = SocialProfileExistSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            social_id = request.data.get("social_id")
            username = request.data.get("username")
            email = request.data.get("email")
            data = social_account_exist(username,social_id,email)
            return Response(data={
                "statusCode": 200, "error": False,
                "message": "Social Profile Exist",
                "data": {
                    "create_profile": data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class UsersDelete(APIView):
    permission_classes = (IsAdminUser,)

    def delete(self, request):
        """
        Delete single user

        parameter : User id
        Authentication : None
        """
        try:
            ids = request.data.get('ids')
            if not ids:
                message = {"message": {"user ids required"}}
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": message}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            users_not_found = []
            users_exists = []
            for user_id in ids:
                user_obj_check = User.objects.filter(id=user_id).exists()
                if not user_obj_check:
                    users_not_found.append(user_id)
                if user_obj_check:
                    profile = User.objects.filter(id=user_id).first().profile_pic
                    delete_image(profile.name.split("/")[1])
                    users_exists.append(user_id)
                user = User.objects.get(id=user_id)
                user_remove_mongo(user)
                # Friend.objects.filter(Q(user=user) | Q(friend=user)).delete()
                # dbname = get_mongodb_database()
                # collection_name = dbname["SeanCollection"]
                # collection_name.delete_one({"user_id": user.id})
                # user_found_in_friend_list = collection_name.find({"friends_list": user.id}, {'_id': 0})
                # for i in user_found_in_friend_list:
                #     if user.id in i.get("friends_list"):
                #         i.get("friends_list").remove(user.id)
                #         friends_list = i.get("friends_list")
                #         values = {"$set": {"friends_list": friends_list}}
                #         update_friend_list = collection_name.find({"user_id": i.get("user_id")})
                #         myquery = update_friend_list[0]
                #         collection_name.update_one(myquery, values)
                # friend list update
                User.objects.filter(id=user_id).delete()
            message_not_exists = {"user_ids": ["Object with ids={} does not exist.".format(users_not_found)]}
            message_exists = {"user_ids": ["Object with ids={} deleted successfully.".format(users_exists)]}
            response = {"statusCode": 200, "error": False,
                        "not_found": message_not_exists, "message": message_exists}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)