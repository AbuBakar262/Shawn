from event.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from sean_backend.utils import PermissionsUtil


# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

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
        response = {"statusCode": 201, "error": False, "message": "Event Submitted Successfully!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        query = Event.objects.filter(user=request.user).order_by('-id')
        serializer = EventListSerializer(query, many=True)
        response = {"statusCode": 200, "error": False, "message": "User Event List!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventListSerializer(instance)
        response = {"statusCode": 200, "error": False, "message": "Get Event!", "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        response = {"statusCode": 200, "error": False, "message": "Event successfully updated!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PermissionsUtil.permission(request, instance)
        self.perform_destroy(instance)
        response = {"statusCode": 200, "error": False, "message": "Event successfully deleted!", "data": ""}
        return Response(response, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

    def all_events(self, request):
        query = Event.objects.all().exclude(is_hide=True).order_by('-id')
        serializer = EventListSerializer(query, many=True)
        response = {"statusCode": 200, "error": False, "message": "All Event List!",
                    "data": serializer.data}
        return Response(response, status=status.HTTP_201_CREATED)

    def get_event(self, request, *args, **kwargs):
        serializer = GetEventSerializer(data=request.query_params)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        instance = self.request.query_params.get('event')
        if not Event.objects.filter(id=instance, is_hide=True).exists():
            query = Event.objects.filter(id=instance).first()
            serializer = EventListSerializer(query, many=False)
            response = {"statusCode": 200, "error": False, "message": "Get Event!", "data": serializer.data}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"statusCode": 200, "error": False, "message": "Event does not exist!"}
            return Response(response, status=status.HTTP_200_OK)

    def hide_event(self, request, *args, **kwargs):

        serializer = HideEventSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        event = request.data.get("event")
        hide = request.data.get("hide")
        instance = Event.objects.get(id=event)
        PermissionsUtil.permission(request, instance)
        instance.is_hide = hide
        instance.save()
        response = {"statusCode": 200, "error": False, "message": "Event successfully hide!"}
        return Response(response, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['all_events'] or self.action in ['get_event']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
