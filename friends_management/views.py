from django.db.models import Q
from accounts.models import *
from accounts.serializers import UserProfileSerializer
from friends_management.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from notification.models import DeviceRegistration
from sean_backend.utils import notification

# Create your views here.


class FriendManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def contact_list(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
            friend_list = Friend.objects.filter(user=user)
            friend_list = [friend.friend.id for friend in friend_list]
            reject_list = RejectRequest.objects.filter(user=user)
            reject_list = [reject.rejected_user.id for reject in reject_list]
            if BlockUser.objects.filter(user=user).exists():
                block_list = BlockUser.objects.filter(user=user)
                block_list = [block.block_user.id for block in block_list]
            else:
                block_list = []
            if BlockUser.objects.filter(block_user=user).exists():
                block_list1 = BlockUser.objects.filter(block_user=user)
                block_list1 = [block.user.id for block in block_list1]
                block_list = block_list + block_list1
            else:
                block_list1 = []
            block_list = block_list + block_list1
            contact_list = User.objects.exclude(id__in=friend_list).exclude(id__in=reject_list).exclude(
                id=user.id).exclude(is_superuser=True).exclude(id__in=block_list).exclude(create_profile=False)
            serializer = UserProfileSerializer(contact_list, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Contact List",
                "result": serializer.data,
                "total": contact_list.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def all_user_list(self, request, *args, **kwargs):
        try:
            user = request.user
            user_block_to = BlockUser.objects.filter(user=user).values_list("block_user", flat=True)
            user_block_by = BlockUser.objects.filter(block_user=user).values_list("user", flat=True)
            all_user = User.objects.exclude(id=user.id).exclude(is_superuser=True). \
                exclude(id__in=user_block_to).exclude(id__in=user_block_by).exclude(create_profile=False)
            serializer = FriendSerializer(all_user, many=True)
            return Response({
                "statusCode": 200, "error": False, "message": "All User List",
                "data": serializer.data, "total": all_user.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "statusCode": 400, "error": True,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def send_friend_request(self, request, *args, **kwargs):
        try:
            user = request.user
            friend = User.objects.get(id=request.data.get("friend_request"))
            if not friend:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            friend_request = FriendRequest.objects.filter(user=user, receiver_friend_request=friend).first()
            if friend_request:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend request already sent"
                }, status=status.HTTP_400_BAD_REQUEST)
            existing_friend = Friend.objects.filter(user=user, friend=friend).first()
            if existing_friend:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Already friends"
                }, status=status.HTTP_400_BAD_REQUEST)
            if user == friend:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You can't send friend request to yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            if friend.is_account == "Public":
                Friend.objects.create(user=user, friend=friend)
                registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
                notification(device_id=registration_id, title="Friend",
                             body="{} is now your friend".format(user.username))
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request accepted",
                    "data": {
                        "user": UserSerializer(user).data,
                        "friend": UserSerializer(friend).data
                    }
                }, status=status.HTTP_200_OK)
            friend_request = FriendRequest.objects.create(user=user, receiver_friend_request=friend)
            registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
            notification(device_id=registration_id, title="Friend Request", body="{} sent you friend request".format(user.username))
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request sent successfully",
                    "data": {
                        "user": UserSerializer(friend_request.user).data,
                        "friend": UserSerializer(friend_request.receiver_friend_request).data
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

    def friend_request_list(self, request, *args, **kwargs):
        try:
            user = request.user
            friend_request = FriendRequest.objects.filter(receiver_friend_request=user)
            serializer = FriendRequestListSerializer(friend_request, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Friend Request List",
                "responsePayload": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_action(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = FriendRequestActionSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            friend_request_id = serializer.validated_data['friend_request']
            friend_request = FriendRequest.objects.filter(id=friend_request_id.id).first()
            if not friend_request:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend request not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            if friend_request.receiver_friend_request != user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You are not authorized to perform this action"
                }, status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['status'] == 'accepted':
                Friend.objects.create(user=friend_request.user, friend=friend_request.receiver_friend_request)
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request accepted"
                }, status=status.HTTP_200_OK)
            elif serializer.validated_data['status'] == 'rejected':
                RejectRequest.objects.create(user=friend_request.user,
                                             rejected_user=friend_request.receiver_friend_request)
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request rejected"
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid status"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_delete(self, request, *args, **kwargs):
        try:
            user = request.user
            friend_request = FriendRequest.objects.filter(id=request.data['friend_request_id']).first()
            if not friend_request:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend request not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            if friend_request.sender == user:
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request deleted successfully"
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You are not authorized to perform this action"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_list(self, request, *args, **kwargs):
        try:
            user = request.user
            user_friend = Friend.objects.filter(user=user).values_list("friend", flat=True)
            friend_user = Friend.objects.filter(friend=user).values_list("user", flat=True)
            total = user_friend.count() + friend_user.count()
            users = User.objects.filter(Q(id__in=user_friend) | Q(id__in=friend_user))
            serializer = FriendSerializer(users, many=True)
            return Response(data={
                "statusCode": 200, "error": False,
                "message": "Friend List fetched successfully",
                "data": serializer.data,
                "total": total
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "error": True,
                "statusCode": 400,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_delete(self, request, *args, **kwargs):
        try:
            user = request.user
            friend = User.objects.filter(id=request.data['friend_id']).first()
            if not friend:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            if Friend.objects.filter(user=user, friend=friend):
                Friend.objects.filter(user=user, friend=friend).delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend deleted successfully"
                }, status=status.HTTP_200_OK)
            elif Friend.objects.filter(user=friend, friend=user):
                Friend.objects.filter(user=friend, friend=user).delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend deleted successfully"
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend not found"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
