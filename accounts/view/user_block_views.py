from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, BlockUser
from accounts.serializer.user_block_serializers import BlockUserSerializer
from accounts.serializer.signin_serializers import UserSerializer
from accounts.serializer.user_profile_serializers import UserProfileUpdateSerializer


# user block/unblock other user and this user can not see blocked user
class BlockUserViewSet(ModelViewSet):
    queryset = BlockUser.objects.all()
    serializer_class = BlockUserSerializer
    permission_classes = [IsAuthenticated]

    def block_user(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user = User.objects.get(id=request.data.get('user_id'))
            if user == blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You can not block yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            if BlockUser.objects.filter(blocked_user=blocked_user, user=user).exists():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User already blocked"
                }, status=status.HTTP_400_BAD_REQUEST)
            BlockUser.objects.create(
                user=user,
                blocked_user=blocked_user,
                block_by=user
            )
            BlockUser.objects.create(
                user=blocked_user,
                blocked_user=user
            )
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "User blocked successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def blocked_user_list(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user_list = BlockUser.objects.filter(block_by=user)
            blocked_user_serializer = BlockUserSerializer(blocked_user_list, many=True)
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Blocked user list fetched successfully",
                "responsePayload": blocked_user_serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def unblock_user(self, request, *args, **kwargs):
        try:
            user = request.user
            blocked_user = User.objects.get(id=request.data.get('user_id'))
            if user == blocked_user:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You can not unblock yourself"
                }, status=status.HTTP_400_BAD_REQUEST)
            if not BlockUser.objects.filter(blocked_user=blocked_user, user=user).exists():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User not blocked"
                }, status=status.HTTP_400_BAD_REQUEST)
            BlockUser.objects.filter(blocked_user=blocked_user, user=user).delete()
            return Response(data={
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "User unblocked successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
