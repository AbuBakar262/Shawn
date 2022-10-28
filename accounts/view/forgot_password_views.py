from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, VerificationCode
from accounts.serializer.forgot_password_serializers import ForgotPasswordSerializer, ChangePasswordSerializer
from accounts.accounts_utiles.reuseable_methods import send_otp_via_email, random_string_generator
from rest_framework.viewsets import ModelViewSet
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from accounts.serializer.signin_serializers import UserSerializer


class ForgotPasswordViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def forgot_password(self, request, *args, **kwargs):
        try:
            serializer = ForgotPasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=request.data.get('email'))
            link = "http://localhost:3000/accounts/forgot_change_password/" + urlsafe_base64_encode(
                force_bytes(user.pk)) + "/" + PasswordResetTokenGenerator().make_token(user) + "/"
            send_otp_via_email(request.data.get('email'), link)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Reset password link sent to your email",
                        "responsePayload": serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e),
                     "responsePayload": None}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)


class ForgotChangePasswordViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [AllowAny]

    def forgot_change_password(self, request, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(kwargs['uidb64']).decode()
            if not User.objects.filter(pk=uid).exists():
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "User does not exist",
                    "responsePayload": None
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(pk=uid)
            if not PasswordResetTokenGenerator().check_token(user, kwargs['token']):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid token",
                    "responsePayload": None
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = ChangePasswordSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if user.check_password(request.data.get('password')):
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Your new password must be different from the old password",
                }, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('password'))
            user.save()
            user_serializer = UserSerializer(user)
            response = {"status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Password changed successfully",
                        "responsePayload": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"status": "error",
                     "status_code": status.HTTP_400_BAD_REQUEST,
                     "message": str(e),
                     "responsePayload": None}
            return Response(data=error, status=status.HTTP_400_BAD_REQUEST)
