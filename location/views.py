import json

import requests

from location.serializers import *
from rest_framework import viewsets, generics, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from sean_backend.settings import GOOGLE_MAPS_URL, GOOGLE_MAPS_RADIUS, GOOGLE_MAPS_TYPES, GOOGLE_MAPS_KEYWORDS, \
    GOOGLE_MAPS_API_KEY
from sean_backend.utils import PermissionsUtil


# Create your views here.

class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = FavouriteLocation.objects.all()
    serializer_class = UserLocationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={"request": request})
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

    def search_location(self, request, *args, **kwargs):
        serializer = SearchLocationSerializer(data=request.query_params)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        lat = request.query_params.get("latitude")
        long = request.query_params.get("longitude")
        try:
            url = GOOGLE_MAPS_URL+lat+"%2C"+long+"&"+"radius="+GOOGLE_MAPS_RADIUS+"&"+"type="+GOOGLE_MAPS_TYPES+"&keyword="+GOOGLE_MAPS_KEYWORDS+"&key="+GOOGLE_MAPS_API_KEY
            payload = {}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            response = json.loads(response.text)
            result = []
            if response:
                response_length = response['results']
                if len(response_length) > 10:
                    response_data = response_length[0:10]
                else:
                    response_data = response_length
                for i in response_data:
                    data = {}
                    data['location'] = i.get("geometry").get("location")
                    data['icon'] = i.get("icon")
                    data['name'] = i.get("name")
                    data['opening_hours'] = i.get("opening_hours")
                    data['photos'] = i.get("photos")
                    data['place_id'] = i.get("place_id")
                    data['rating'] = i.get("rating")
                    data['reference'] = i.get("reference")
                    data['scope'] = i.get("scope")
                    data['types'] = i.get("types")
                    data['user_ratings_total'] = i.get("user_ratings_total")
                    data['vicinity'] = i.get("vicinity")
                    latitude = i.get("geometry").get("location").get("lat")
                    longitude = i.get("geometry").get("location").get("lng")
                    data['total'] = CheckInLocation.objects.filter(latitude=latitude, longitude=longitude).count()
                    user_friend = Friend.objects.filter(user=request.user).values_list("friend_id", flat=True)
                    friend_user = Friend.objects.filter(friend=request.user).values_list("user_id", flat=True)
                    friends_list = list(user_friend) + (list(friend_user))
                    data['total_friends'] = CheckInLocation.objects.filter(user_id__in=friends_list,latitude=latitude, longitude=longitude).count()
                    result.append(data)
            else:
                result = []
            response = {"statusCode": 200, "error": False, "message": "Search Location List!",
                        "data": result}
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

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

