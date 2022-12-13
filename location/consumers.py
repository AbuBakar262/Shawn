import json
from channels.generic.websocket import AsyncWebsocketConsumer
from pymongo import MongoClient
from sean_backend.settings import MONGODB_CONNECTING_STRING


def get_mongodb_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    # CONNECTION_STRING = MONGODB_CONNECTING_STRING

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient('mongodb+srv://ali:123@cluster0.nkjzhzh.mongodb.net/?retryWrites=true&w=majority')
    # print(client['TestDB'])
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['TestDB']


def update_location(user_id, latitude, longitude, profile_thumbnail, friends_list):
        latitude = latitude
        longitude = longitude
        dbname = get_mongodb_database()
        collection_name = dbname["SeanCollection"]
        list_index_check = list(collection_name.list_indexes())
        if len(list_index_check) == 0:
            collection_name.create_index([("location", "2dsphere")])
        index_check = collection_name.index_information()
        if index_check:
            get_index = index_check.get('location_2dsphere')
            if get_index is None:
                collection_name.create_index([("location", "2dsphere")])
        found = collection_name.find({"user_id": user_id})
        try:
            driver_mongo = list(found)
        except:
            driver_mongo = []
        if len(driver_mongo) == 0:
            collection_name.insert_one(
                {"user_id": user_id, "profile_thumbnail": profile_thumbnail, "friends_list":friends_list,
                 "location": {"type": "Point", "coordinates": [float(longitude), float(latitude)],},
                 "upsert": True,
                 })
        else:
            myquery = driver_mongo[0]
            new_values = {"$set": {"profile_thumbnail": profile_thumbnail, "friends_list":friends_list,
                 "location": {"type": "Point", "coordinates": [float(longitude), float(latitude)],},
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