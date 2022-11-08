from accounts.models import User
from event.models import Event
from event.serializers import EventSerializer, EventListSerializer, UpdateEventSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EventListSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(data=request.data, context={'request': request})
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
                'message': 'Event created successfully',
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
            event_id = kwargs.get('pk')
            event = Event.objects.get(id=event_id)
            serializer = self.get_serializer(event)
            if user != event.user:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'You are not authorized to view this event'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Event fetched successfully',
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
            events = Event.objects.filter(user=user)
            serializer = self.get_serializer(events, many=True)
            if not serializer.data:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Event not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Events fetched successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            user = request.user
            event_id = kwargs.get('pk')
            event = Event.objects.get(id=event_id)
            serializer = self.get_serializer(event, data=request.data, context={'request': request})
            if not serializer.is_valid():
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            if user != event.user:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'You are not authorized to update this event'
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Event updated successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            user = request.user
            event_id = kwargs.get('pk')
            event = Event.objects.get(id=event_id)
            if user != event.user:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'You are not authorized to delete this event'
                }, status=status.HTTP_400_BAD_REQUEST)
            event.delete()
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Event deleted successfully',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def all_events(self, request, *args, **kwargs):
        try:
            events = Event.objects.all().exclude(is_hide=True)
            serializer = self.get_serializer(events, many=True)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Events fetched successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_event(self, request, *args, **kwargs):
        try:
            event_id = kwargs.get('pk')
            event = Event.objects.get(id=event_id)
            serializer = EventListSerializer(event)
            if event.is_hide:
                return Response({
                    'status': False,
                    'status_code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Event not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Event fetched successfully',
                'result': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action in ['all_events'] or self.action in ['get_event']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

