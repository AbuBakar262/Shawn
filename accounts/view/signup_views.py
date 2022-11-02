from accounts.models import User, VerificationCode
from accounts.serializer.signup_serializers import SignupSerializer, VerifySerializer
from accounts.serializer.signin_serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class SignupViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
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
                "responsePayload": serializer.data['user']
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = VerifySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = VerifySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            verification_code = VerificationCode.objects.get(user=user)
            if verification_code.code == request.data.get('code'):
                user.is_verified = True
                user.save()
                verification_code.delete()
            user_serializer = UserSerializer(user)
            refresh = RefreshToken.for_user(user)
            access = AccessToken.for_user(user)
            return Response(data={'message': 'User verified successfully',
                                  'responsePayload': {'user': user_serializer.data,
                                                      'refresh': str(refresh),
                                                      'access': str(access)}},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
