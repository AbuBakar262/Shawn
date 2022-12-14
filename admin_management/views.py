from accounts.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from admin_management.models import ReportUser, Subscription
from admin_management.serializers import (
    AdminLoginSerializer, CreateReportUserSerializer, ListReportUserSerializer,
    UpdateReportUserSerializer, AdminListUserSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class AdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def login(self, request, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        data = UserSerializer(user).data
        data['access'] = str(AccessToken.for_user(user))
        data['refresh'] = str(RefreshToken.for_user(user))
        response = {"statusCode": 200, "error": False, "message": "Admin Login successfully!", "data": data}
        return Response(response, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.exclude(is_superuser=True)
            user_serializer = UserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "User List", "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ReportUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateReportUserSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            response = {"statusCode": 200, "error": False, "message": "User Reported Successfully!",
                                                                                        "data": serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            report_id = request.GET.get('report_id')
            report = ReportUser.objects.get(id=report_id)
            serializer = UpdateReportUserSerializer(report, data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            response = {"statusCode": 200, "error": False, "message": "Report Updated Successfully!",
                                                                                        "data": serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class ListReportUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        try:
            user = ReportUser.objects.all()
            user_serializer = ListReportUserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "User List", "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def get_by_id(self, request, *args, **kwargs):
        try:
            report_id = request.GET.get('report_id')
            report = ReportUser.objects.get(id=report_id)
            serializer = ListReportUserSerializer(report)
            response = {"statusCode": 200, "error": False, "message": "User List", "data": serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class AdminListUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    """
        This class has 4 Apis and only admin can view these lists:
        -> Subscribed Users List
        -> Un-Subscribed Users List
        -> Trial Base Users List
        -> All Users List
    """

    def subscribed_user_list(self, request, *args, **kwargs):
        try:
            user = Subscription.objects.filter(status='subscribed')
            user_serializer = AdminListUserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "Subscribed User List",
                        "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def unsubscribed_user_list(self, request, *args, **kwargs):
        try:
            user = Subscription.objects.filter(status='unsubscribed')
            user_serializer = AdminListUserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "UnSubscribed User List",
                        "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def trial_user_list(self, request, *args, **kwargs):
        try:
            user = Subscription.objects.filter(status='trial')
            user_serializer = AdminListUserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "Trial User List", "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def list_all_users(self, request, *args, **kwargs):
        try:
            user = Subscription.objects.all()
            user_serializer = AdminListUserSerializer(user, many=True)
            response = {"statusCode": 200, "error": False, "message": "All User List", "data": user_serializer.data}
            return Response(data=response, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": str(e)}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
