import json
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.permissions import IsAuthenticated

from location.utils import update_location


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
        user = self.scope['user']
        print("received")
        latitude = text_data_json['latitude']
        longitude = text_data_json['longitude']
        update_location(user, latitude, longitude)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'result': text_data_json,
                # 'lat': lat,
                # 'long': long,
                # 'job_id': job_id
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # lat = event['lat']
        # long = event['long']
        # job_id = event['job_id']
        result = event['result']
        print("send")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'result': result,
            # 'lat': lat,
            # 'long': long,
            # 'job_id': job_id
        }))
