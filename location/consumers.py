# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from sean_backend.settings import MONGODB_CONNECTING_STRING, MONGODB_NAME, COLLECTION_NAME
# from pymongo import MongoClient, GEO2D
#
# def get_mongodb_database():
#     # Provide the mongodb atlas url to connect python to mongodb using pymongo
#     CONNECTION_STRING = MONGODB_CONNECTING_STRING
#
#     # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
#     client = MongoClient(CONNECTION_STRING)
#
#     # Create the database for our example (we will use the same database throughout the tutorial
#     return client[MONGODB_NAME]
#
#
# def update_location(user_id, latitude, longitude, profile_thumbnail, friends_list):
#     dbname = get_mongodb_database()
#     print(dbname)
#     collection_name = dbname[COLLECTION_NAME]
#     print("start collection")
#     list_index_check = list(collection_name.list_indexes())
#     print("after DB")
#     if len(list_index_check) == 0:
#         collection_name.create_index([("TestCollection", GEO2D)])
#     index_check = collection_name.index_information()
#     if index_check:
#         get_index = index_check.get('TestCollection_2d')
#         if get_index is None:
#             collection_name.create_index([("TestCollection", GEO2D)])
#     user_id = user_id
#     profile_thumbnail = profile_thumbnail
#     friends_list = friends_list
#     latitude = latitude
#     longitude = longitude
#
#     user_found = collection_name.find({"user_id": user_id})
#     user_in_db = list(user_found)
#     if len(user_in_db) == 0:
#         collection_name.insert_one({"user_id": user_id, "profile_thumbnail": profile_thumbnail,
#                                     "friend_ids": friends_list,
#                                     "location": [float(latitude), float(longitude)]})
#     else:
#         print("before query")
#         myquery = user_in_db[0]
#         new_values = {"$set": {"profile_thumbnail": profile_thumbnail,
#                                "friend_ids": friends_list,
#                                "location": [float(latitude), float(longitude)]}}
#         collection_name.update_one(myquery, new_values)
#
#
# class LiveTrackingConsumer(AsyncWebsocketConsumer):
#     # permission_classes = [IsAuthenticated]
#
#     async def connect(self):
#         # self.user = self.scope["user"]
#         self.room_name = self.scope['url_route']['kwargs']['lat']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#         # await self.channel_layer.group_send(
#         #     self.room_group_name,
#         #     {
#         #         'type':  'chat_message',
#         #         'message_for':  {
#         #         'group':  self.room_group_name,
#         #         'chanels': self.channel_name
#         #     }
#         #     }
#         # )
#
#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         if text_data_json.get("user_id"):
#             # update_location(text_data_json)
#             location = text_data_json
#
#             update_location(location.get('user_id'), location.get('latitude'), location.get('longitude'),
#                             location.get('profile_thumbnail'), location.get('friends_list'), )
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'result': text_data_json,
#             }
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         result = event['result']
#         print("send")
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'result': result,
#         }))



import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pymongo import MongoClient, GEO2D
from rest_framework.response import Response
from sean_backend.settings import MONGODB_CONNECTING_STRING, MONGODB_NAME


def get_mongodb_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = MONGODB_CONNECTING_STRING

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient('mongodb+srv://ali:123@cluster0.nkjzhzh.mongodb.net/?retryWrites=true&w=majority')
    print(client['TestDB'])
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['TestDB']


def update_location(user_id, latitude, longitude, profile_thumbnail, friends_list):
        latitude = latitude
        longitude = longitude
        dbname = get_mongodb_database()
        collection_name = dbname["SeanCollection"]
        list_index_check = list(collection_name.list_indexes())
        if len(list_index_check) == 0:
            # collection_name.create_index([("location", GEO2D)])
            collection_name.create_index([("location", "2dsphere")])
        index_check = collection_name.index_information()
        if index_check:
            get_index = index_check.get('location_2dsphere')
            if get_index is None:
                # collection_name.create_index([("location", GEO2D)])
                collection_name.create_index([("location", "2dsphere")])
        found = collection_name.find({"user_id": user_id})
        driver_mongo = list(found)
        if len(driver_mongo) == 0:
            collection_name.insert_one(
                {"user_id": user_id, "profile_thumbnail": profile_thumbnail, "friends_list":friends_list,
                 "location": {"type": "Point", "coordinates": [float(latitude), float(longitude)],},
                 "upsert": True,
                 })
        else:
            myquery = driver_mongo[0]
            new_values = {"$set": {"profile_thumbnail": profile_thumbnail, "friends_list":friends_list,
                 "location": {"type": "Point", "coordinates": [float(latitude), float(longitude)],},
                                   "upsert": True,}}
            collection_name.update_one(myquery, new_values)


class LiveTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['lat']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        if text_data_json.get('user_id'):
            location = text_data_json
            update_location(location.get('user_id'), location.get('latitude'),
                            location.get('longitude'), location.get('profile_thumbnail'), location.get('friends_list'),)
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