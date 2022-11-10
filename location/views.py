from location.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


# Create your views here.

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserLocationSerializer(data=request.data, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Location saved successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            locations = UserLocation.objects.filter(user=user)
            serializer = UserLocationListSerializer(locations, many=True)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Locations fetched successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            location = self.get_object()
            if user != location.user:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'You are not allowed to view this location'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserLocationListSerializer(location)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Location fetched successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            location = self.get_object()
            if user != location.user:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'You are not allowed to delete this location'
                }, status=status.HTTP_400_BAD_REQUEST)
            location.delete()
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Location deleted successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)