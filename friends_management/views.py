import json

from django.db.models import Q
from accounts.models import *
from accounts.serializers import UserProfileSerializer
from friends_management.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from location.serializers import SearchLocationSerializer
from notification.models import *

from location.utils import get_mongodb_database
# from notification.models import DeviceRegistration
from sean_backend.utils import firebase_notification


# Create your views here.


class FriendManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddFriendSerializer
    queryset = Friend.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(user=user)
            friend = serializer.data.get("friend")
            registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
            notification = firebase_notification(device_id=registration_id, title="Friend", body="{} is now your friend".format(user.username))
            if notification == True:
                receiver = User.objects.filter(id=friend).first()
                Notification.objects.create(sender=user, receiver=receiver, type="Add Friend")
                response = {"statusCode": 200, "error": False, "message": "Friend Added Successfully!",
                            "data": serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                receiver = User.objects.filter(id=friend).first()
                Notification.objects.create(sender=user, receiver=receiver, type="Add Friend")
                response = {"statusCode": 200, "error": False, "message": "Friend Added Successfully, but issue in notification, notification not sent!",
                            "data": serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request, *args, **kwargs):
        serializer = SearchLocationSerializer(data=request.query_params)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        try:
            user = request.user
            dbname = get_mongodb_database()
            collection_name = dbname["SeanCollection"]
            query = {"friends_list": user.id, "location": {"$near": {"$geometry": {"type": "Point", "coordinates":
                [float(latitude), float(longitude)], }, "$maxDistance": 15000, }, }, }, {'_id': 0}
            user_found = list(collection_name.find(query))
            # user_found = list(collection_name.find({"friends_list": user.id}, {'_id': 0}))
            return Response(data={
                "statusCode": 200, "error": False,
                "message": "All Friends List",
                "data": user_found,
                "found_people": len(user_found)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def contact_list(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.user.id)
            friend_list = Friend.objects.filter(user=request.user).values_list("friend_id", flat=True)
            reject_list = RejectRequest.objects.filter(user=request.user).values_list("rejected_user_id", flat=True)
            user_block_list = []
            block_user = BlockUser.objects.filter(user=request.user).values_list("block_user_id", flat=True)
            user_block = BlockUser.objects.filter(block_user=request.user).values_list("user_id", flat=True)
            user_block_list.extend(block_user)
            user_block_list.extend(user_block)
            contact_list = User.objects.exclude(id__in=friend_list).exclude(id__in=reject_list).exclude(
                id=user.id).exclude(is_superuser=True).exclude(id__in=user_block_list).exclude(create_profile=False)
            serializer = UserProfileSerializer(contact_list, many=True)
            return Response({
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Contact List",
                "result": serializer.data,
                "total": contact_list.count()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def all_user_list(self, request, *args, **kwargs):
        try:
            serializer = SearchLocationSerializer(data=request.query_params)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            latitude = request.query_params.get("latitude")
            longitude = request.query_params.get("longitude")
            # user = request.user
            dbname = get_mongodb_database()
            collection_name = dbname["SeanCollection"]
            query = {"location": {"$near": {"$geometry": {"type": "Point", "coordinates":
                [float(latitude), float(longitude)], }, "$maxDistance": 15000, }, }, }
            user_found = list(collection_name.find(query))
            # user_found = list(collection_name.find({},{'_id':0}))
            return Response({
                "statusCode": 200, "error": False, "message": "All Users List",
                "data": user_found,
                "found_people": len(user_found)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def send_friend_request(self, request, *args, **kwargs):
        try:
            serializer = FriendRequestSerializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend = request.data.get("friend_request")
            receiver = User.objects.filter(id=friend).first()
            friend_request = Notification.objects.create(sender=user, receiver=receiver, type="Send Request")
            registration_id = DeviceRegistration.objects.filter(user=friend).first().registration_id
            notification = firebase_notification(device_id=registration_id, title="Friend Request",
                                                 body="{} sent you friend request".format(user.username))
            if notification == True:
                return Response(
                    data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Friend request sent successfully",
                        "data": {
                            "user": friend_request.sender.id,
                            "friend": friend_request.receiver.id
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={
                        "status": "success",
                        "status_code": status.HTTP_200_OK,
                        "message": "Friend request sent successfully, but issue in notification, notification not sent",
                        "data": {
                            "user": friend_request.sender.id,
                            "friend": friend_request.receiver.id
                        }
                    },
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_action(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = FriendRequestActionSerializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            notification_id = request.data.get("friend_request")
            sender = request.data.get("friend_request_sender")
            status_type = request.data.get('status')
            friend_request = Notification.objects.filter(id=notification_id, sender=sender).first()
            if status_type == 'Accepted':
                Friend.objects.create(user=friend_request.sender, friend=friend_request.receiver)
                Notification.objects.create(sender=friend_request.receiver, receiver=friend_request.sender, type="Accept Request")
                registration_id = DeviceRegistration.objects.filter(user=friend_request.sender).first().registration_id
                notification = firebase_notification(device_id=registration_id, title="Friend",
                                                     body="{} is now your friend".format(user.username))
                friend_request.delete()
                if notification == True:
                    return Response(data={
                        "statusCode": 200, "error": False,
                        "message": "Friend request accepted",
                        "data": {}
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(data={
                        "statusCode": 200, "error": False,
                        "message": "Friend request accepted, but issue in notification, notification not sent",
                        "data": {}
                    }, status=status.HTTP_200_OK)
            else:
                RejectRequest.objects.create(user=friend_request.sender,
                                             rejected_user=friend_request.receiver)
                friend_request.delete()
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "Friend request rejected",
                    "data": {}
                }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def friend_request_delete(self, request, *args, **kwargs):
        try:
            serializer = FriendRequestDeleteSerializer(data=request.data)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend_request = Notification.objects.filter(id=request.data.get('friend_request_id').id).first()
            if friend_request.sender == user:
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Friend request deleted successfully"
                }, status=status.HTTP_200_OK)
            if friend_request.receiver == user:
                friend_request.delete()
                return Response(data={
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Notification deleted successfully"
                }, status=status.HTTP_200_OK)
            else:
                return Response(data={
                    "status": "error",
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "You are not authorized to perform this action"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def unfriend(self, request, *args, **kwargs):
        try:
            serializer = UnFriendSerializer(data=request.data, context={"request": request})
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                         "errors": e.args[0]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            friend = request.data.get('friend')
            if Friend.objects.filter(Q(user=user, friend=friend) | Q(user=friend, friend=user)).exists():
                Friend.objects.filter(Q(user=user, friend=friend) | Q(user=friend, friend=user)).delete()
                user_friend = Friend.objects.filter(user=user).values_list("friend_id", flat=True)
                friend_user = Friend.objects.filter(friend=user).values_list("user_id", flat=True)
                friends_list = list(user_friend) + (list(friend_user))
                dbname = get_mongodb_database()
                collection_name = dbname["SeanCollection"]
                user_found = list(collection_name.find({"user_id": user.id}, {'_id': 0}))
                myquery = user_found[0]
                new_values = {"$set": {"friends_list": friends_list}}
                collection_name.update_one(myquery, new_values)
                return Response(data={
                    "statusCode": 200, "error": False,
                    "message": "UnFriend successfully",
                    "data": {}
                }, status=status.HTTP_200_OK)
        except Exception as e:
            error = {"statusCode": 400, "error": True, "data": "", "message": "Bad Request, Please check request",
                     "errors": e.args[0]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
