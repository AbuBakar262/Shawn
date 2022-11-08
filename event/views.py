from accounts.models import User
from event.models import UserLocation
from event.serializers import (UserLocationSerializer, UserLocationListSerializer)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    permission_classes = [IsAuthenticated]

    def save_location(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserLocationSerializer(data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
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

    def saved_locations(self, request, *args, **kwargs):
        try:
            user = request.user
            locations = UserLocation.objects.filter(user=user)
            serializer = UserLocationListSerializer(locations, many=True)
            if not serializer.data:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Location not found'
                }, status=status.HTTP_400_BAD_REQUEST)
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

    def get_location(self, request, *args, **kwargs):
        try:
            user = request.user
            location = request.data.get('location')
            location = UserLocation.objects.filter(user=user, id=location).first()
            if location is None:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Location not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserLocationListSerializer(location)
            if not serializer.data:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'No event found'
                }, status=status.HTTP_400_BAD_REQUEST)
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

    def delete_location(self, request, *args, **kwargs):
        try:
            user = request.user
            location = request.data.get('location')
            location = UserLocation.objects.filter(user=user, id=location).first()
            if location is None:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Location not found'
                }, status=status.HTTP_400_BAD_REQUEST)
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
