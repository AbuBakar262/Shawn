from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, Location
from accounts.serializer.location_serializers import LocationSerializer, UserLocationsSerializer
from accounts.serializer.signin_serializers import UserSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def location(self, request, *args, **kwargs):
        try:
            user = request.user
            if Location.objects.filter(user=user).exists():
                location = Location.objects.get(user=user)
                serializer = LocationSerializer(location, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        data={
                            "status": "success",
                            "status_code": status.HTTP_200_OK,
                            "message": "Location updated successfully",
                            "responsePayload": serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(data={
                        "status": "error",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = LocationSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=user)
                    return Response(
                        data={
                            "status": "success",
                            "status_code": status.HTTP_200_OK,
                            "message": "Location saved successfully",
                            "responsePayload": serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(data={
                        "status": "error",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    # show all user location with their id
    def location_list(self, request, *args, **kwargs):
        try:
            locations = Location.objects.all()
            serializer = UserLocationsSerializer(locations, many=True)
            return Response(
                data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Location list fetched successfully",
                    "responsePayload": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

