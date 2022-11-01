from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.models import User, Location
from accounts.serializer.location_serializers import LocationSerializer
from accounts.serializer.signin_serializers import UserSerializer
from ip2geotools.databases.noncommercial import DbIpCity


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def location(self, request, *args, **kwargs):
        try:
            user = request.user
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            response = DbIpCity.get(ip, api_key='free')
            if Location.objects.filter(user=user).exists():
                location = Location.objects.get(user=user)
                location_serializer = LocationSerializer(location, data={
                    "user": user.id,
                    "ip": ip,
                    "latitude": response.latitude,
                    "longitude": response.longitude,
                    "city": response.city,
                    "country": response.country
                })
                if location_serializer.is_valid():
                    location_serializer.save()
                    return Response(data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Location updated successfully"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(data={
                        "status": "error",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": location_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                location_serializer = LocationSerializer(data={
                    "user": user.id,
                    "ip": ip,
                    "latitude": response.latitude,
                    "longitude": response.longitude,
                    "city": response.city,
                    "country": response.country
                })
                if location_serializer.is_valid():
                    location_serializer.save()
                    return Response(data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Location created successfully"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(data={
                        "status": "error",
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": location_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
