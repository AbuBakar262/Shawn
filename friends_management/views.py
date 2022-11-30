from itertools import chain

from django.db.models import Q
from accounts.models import *
from accounts.serializers import UserProfileSerializer
from friends_management.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from notification.models import *
from sean_backend.utils import notification


# Create your views here.


class FriendManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def contact_list(self, request, *args, **kwargs):
        try:
            friend_list = Friend.objects.filter(user=request.user).values_list("id", flat=True)
            reject_list = RejectRequest.objects.filter(user=request.user).values_list("id", flat=True)
            if BlockUser.objects.filter(user=request.user).exists():
                block_list = BlockUser.objects.filter(user=request.user).values_list("id", flat=True)
            else:
                block_list = []
            if BlockUser.objects.filter(block_user=request.user).exists():
                block_list1 = BlockUser.objects.filte(user=request.user).values_list("id", flat=True)
                block_list = list(chain(block_list, block_list1))
            else:
                block_list1 = []
            block_list = list(chain(block_list, block_list1))
            contact_list = User.objects.exclude(id__in=friend_list).exclude(id__in=reject_list).exclude(
                id=request.user.id).exclude(is_superuser=True).exclude(id__in=block_list).exclude(create_profile=False)
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
            serializer = FriendRequestSerializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend = User.objects.get(id=request.data.get("friend_request"))
            if friend.is_account == "Public":
                Friend.objects.create(user=user, friend=friend)
                friend_request = Notification.objects.create(sender=user, receiver=friend, type="Add Friend")
                registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
                notification(device_id=registration_id, title="Friend",
                             body="{} is now your friend".format(user.username))
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "{} added you as friend!".format(user.username),
                    "data": {
                        "user": UserSerializer(friend_request.sender).data,
                        "friend": UserSerializer(friend_request.receiver).data
                    }
                }, status=status.HTTP_200_OK)
            friend_request = Notification.objects.create(sender=user, receiver=friend, type="Send Request")
            registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
            notification(device_id=registration_id, title="Friend Request", body="{} sent you friend request".format(user.username))
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request sent successfully",
                    "data": [{
                        "user": friend_request.sender.id,
                        "friend": friend_request.receiver.id,
                        "friend_request_id": friend_request.id
                    }]
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def notification_list(self, request, *args, **kwargs):
        try:
            user = request.user
            friend_request = Notification.objects.filter(receiver=user)
            serializer = FriendRequestListSerializer(friend_request, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Notification List",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_action(self, request, *args, **kwargs):
        try:
            serializer = FriendRequestActionSerializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            friend_request_id = Notification.objects.get(id=request.data.get("friend_request"))
            friend_request_sender = User.objects.get(id=request.data.get("friend_request_sender"))
            status_type = request.data.get('status')
            friend_request = Notification.objects.filter(id=friend_request_id.id, sender=friend_request_sender).first()
            if status_type == 'Accepted':
                Friend.objects.create(user=friend_request.sender, friend=friend_request.receiver)
                Notification.objects.create(sender=friend_request.receiver, receiver=friend_request.sender, type="Accept Request")
                registration_id = DeviceRegistration.objects.filter(user=friend_request.sender).first().registration_id
                notification(device_id=registration_id, title="Friend",
                             body="{} is now your friend".format(friend_request.receiver.username))
                friend_request.delete()
                return Response(data={
                    "status": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request accepted"
                }, status=status.HTTP_200_OK)
            elif status_type == 'Rejected':
                RejectRequest.objects.create(user=friend_request.sender,
                                             rejected_user=friend_request.receiver)
                friend_request.delete()
                return Response(data={
                    "status": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request rejected"
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": False,
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid status"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_delete(self, request, *args, **kwargs):
        try:
            serializer = FriendRequestDeleteSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend_request = Notification.objects.get(id=request.data.get('friend_request_id'))
            if friend_request.sender == user:
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request deleted successfully"
                }, status=status.HTTP_200_OK)
            if friend_request.receiver == user:
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Notification deleted successfully"
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
            serializer = FriendDeleteSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend = request.data.get('friend_id')
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
