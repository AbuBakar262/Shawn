from accounts.models import User
from friends_management.models import FriendRequest, Friend, RejectRequest
from friends_management.serializers import (ContactListSerializer, FriendRequestListSerializer, FriendRequestActionSerializer)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            contact_list = User.objects.exclude(id__in=friend_list).exclude(id__in=reject_list).exclude(
                id=user.id).exclude(is_superuser=True)
            serializer = ContactListSerializer(contact_list, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Contact List",
                "result": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
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
            friend_request = FriendRequest.objects.filter(sender=user, receiver=friend).first()
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
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request accepted"
                }, status=status.HTTP_200_OK)
            friend_request = FriendRequest.objects.create(sender=user, receiver=friend)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request sent successfully",
                    # return FriendRequest object
                    "result": FriendRequestListSerializer(friend_request).data
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
            friend_request = FriendRequest.objects.filter(receiver=user)
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
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "result": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            friend_request_id = serializer.validated_data['friend_request']
            friend_request = FriendRequest.objects.filter(id=friend_request_id.id).first()
            if not friend_request:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Friend request not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            if friend_request.receiver != user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You are not authorized to perform this action"
                }, status=status.HTTP_400_BAD_REQUEST)
            if serializer.validated_data['status'] == 'accepted':
                Friend.objects.create(user=friend_request.sender, friend=friend_request.receiver)
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request accepted"
                }, status=status.HTTP_200_OK)
            elif serializer.validated_data['status'] == 'rejected':
                RejectRequest.objects.create(user=friend_request.sender, rejected_user=friend_request.receiver)
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