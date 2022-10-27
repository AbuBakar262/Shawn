from rest_framework import serializers
from accounts.models import User, VerificationCode
from accounts.serializer.signup_serializers import SignupSerializer, VerifySerializer
from accounts.serializer.signin_serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accounts.accounts_utiles.reuseable_methods import send_otp_via_email, random_string_generator


class SignupModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = SignupSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            user = User.objects.get(email=request.data.get('email'))
            verification_code = random_string_generator()
            VerificationCode.objects.create(user=user, code=verification_code)
            send_otp_via_email(request.data.get('email'))
            return Response(data={'message': 'User created successfully and verification code sent to email',
                                  'responsePayload': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = VerifySerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = VerifySerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            verification_code = VerificationCode.objects.get(user=user)
            if verification_code.code == request.data.get('code'):
                user.is_verified = True
                user.save()
                return Response(data={'message': 'User verified successfully',
                                      'responsePayload': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
