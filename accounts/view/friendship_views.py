from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, FriendRequest, Friend
from accounts.serializer.friendship_serializers import FriendsSerializer


class FriendsViewSet(ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendsSerializer
    permission_classes = [IsAuthenticated]

    def friend_list(self, request, *args, **kwargs):
        try:
            user = request.user
            friends = Friend.objects.filter(user=user)
            serializer = FriendsSerializer(friends, many=True)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend list fetched successfully",
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
            Friend.objects.filter(user=user, friend=friend).delete()
            Friend.objects.filter(user=friend, friend=user).delete()
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend deleted successfully",
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
