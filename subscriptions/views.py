from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from .serializers import *
from sean_backend.utils import PermissionsUtil


# Create your views here.

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]

    def Subscribed(self, request, *args, **kwargs):
        try:
            serializer = SubscriptionSerializer(data=request.data, context={'request': request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=request.user)
            response = {"statusCode": 201, "error": False, "message": "Subscription Submitted Successfully!",
                        "data": serializer.data}
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
