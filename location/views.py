from location.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from sean_backend.utils import PermissionsUtil


# Create your views here.

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = FavouriteLocation.objects.all()
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user)
        response = {"statusCode": 201, "error": False, "message": "Location saved successfully!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        query = FavouriteLocation.objects.filter(user=request.user).order_by('-id')
        serializer = UserLocationListSerializer(query, many=True)
        response = {"statusCode": 200, "error": False, "message": "User Saved Location List!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserLocationListSerializer(instance)
        response = {"statusCode": 200, "error": False, "message": "Get Location!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "message": "Location successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()


class CheckInLocationViewSet(viewsets.ModelViewSet):
    queryset = CheckInLocation.objects.all()
    serializer_class = CheckInLocationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=request.user)
        response = {"statusCode": 201, "error": False, "message": "CheckIn Location successfully!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        user = request.user
        query = CheckInLocation.objects.filter(user=user).order_by('-id')
        serializer = CheckInListLocationSerializer(query, many=True)
        response = {"statusCode": 200, "error": False, "message": "User Saved Location List!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)
