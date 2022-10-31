from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, FriendRequest, Friend
from accounts.serializer.friend_request_serializers import FriendRequestSerializer, FriendRequestActionSerializer, \
    FriendRequestListSerializer


class FriendRequestViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def send_friend_request(self, request, *args, **kwargs):
        try:
            user = request.user
            friend = User.objects.filter(id=request.data['friend_id']).first()
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
            FriendRequest.objects.create(sender=user, receiver=friend)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request sent successfully",
                    "responsePayload": request.data
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
            friend_requests = FriendRequest.objects.filter(receiver=user)
            serializer = FriendRequestListSerializer(friend_requests, many=True)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request list fetched successfully",
                    "responsePayload": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(data={
                "status": "error",
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
                    "responsePayload": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            friend_request_id = serializer.validated_data['friend_request_id']
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
                Friend.objects.create(user=friend_request.receiver, friend=friend_request.sender)
                friend_request.delete()
                return Response(
                    data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Friend request accepted successfully",
                        "responsePayload": request.data
                    },
                    status=status.HTTP_200_OK
                )
            elif serializer.validated_data['status'] == 'rejected':
                friend_request.delete()
                return Response(
                    data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Friend request rejected successfully",
                        "responsePayload": request.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid action"
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
            if friend_request.sender == user or friend_request.receiver == user:
                friend_request.delete()
                return Response(
                    data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Friend request deleted successfully",
                        "responsePayload": request.data
                    },
                    status=status.HTTP_200_OK
                )
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