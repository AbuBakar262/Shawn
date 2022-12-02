import json
from channels.generic.websocket import AsyncWebsocketConsumer

def get_mongodb_database():
    from sean_backend.settings import MONGODB_CONNECTING_STRING, MONGODB_NAME
    from pymongo import MongoClient, GEO2D
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = MONGODB_CONNECTING_STRING

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[MONGODB_NAME]
def update_location(latitude, longitude, scope):
    print("start function")
    from pymongo import  GEO2D
    from rest_framework.response import Response
    from friends_management.models import Friend
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from jwt import decode as jwt_decode
    from django.conf import settings
    from accounts.models import User

    try:
        ###############################
        user_token = dict(scope['headers'])[b'token'].decode("utf8")
        scope["query_string"] = "token=" + user_token

        token = user_token

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            AccessToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            user = decoded_data["user_id"]
            scope['user'] = user
        ##############################
        if User.objects.filter(id=user).exists():
            user_data = User.objects.filter(id=user).first()
            if user_data.profile_thumbnail:
                profile_thumbnail = user_data.profile_thumbnail.url
            else:
                profile_thumbnail = ""
            user_friend = Friend.objects.filter(user_id=user_data.id).values_list("friend_id", flat=True)
            friend_user = Friend.objects.filter(friend_id=user_data.id).values_list("user_id", flat=True)
            friends_list = list(user_friend) + (list(friend_user))
            latitude = latitude
            longitude = longitude
            dbname = get_mongodb_database()
            collection_name = dbname["TestCollection"]
            list_index_check = list(collection_name.list_indexes())
            if len(list_index_check) == 0:
                collection_name.create_index([("TestCollection", GEO2D)])
            index_check = collection_name.index_information()
            if index_check:
                get_index = index_check.get('TestCollection_2d')
                if get_index is None:
                    collection_name.create_index([("TestCollection", GEO2D)])

            user_found = collection_name.find({"user_id": user})
            user_in_db = list(user_found)
            if len(user_in_db) == 0:
                collection_name.insert_one({"user_id": user, "profile_thumbnail": profile_thumbnail,
                                            "friend_ids": friends_list,
                                            "location": [float(latitude), float(longitude)]})
            else:
                print("before query")
                myquery = user_in_db[0]
                new_values = {"$set": {"user_id": user, "profile_thumbnail": profile_thumbnail,
                                       "friend_ids": friends_list,
                                       "location": [float(latitude), float(longitude)]}}
                result = collection_name.update_one(myquery, new_values)
                print("after query")
                print("done", result.acknowledged)
                print("end function")

    except Exception as e:
        error = {"status": False, "message": e.args[0]}
        return Response(error)

class LiveTrackingConsumer(AsyncWebsocketConsumer):
    # permission_classes = [IsAuthenticated]

    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['lat']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type':  'chat_message',
        #         'message_for':  {
        #         'group':  self.room_group_name,
        #         'chanels': self.channel_name
        #     }
        #     }
        # )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("received")
        latitude = text_data_json['latitude']
        longitude = text_data_json['longitude']
        update_location(latitude, longitude, self.scope)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'result': text_data_json,
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        result = event['result']
        print("send")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'result': result,
        }))
