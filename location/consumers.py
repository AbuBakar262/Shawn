import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from rest_framework.permissions import IsAuthenticated

# from location.utils import update_location


class LiveTrackingConsumer(AsyncWebsocketConsumer):
    # permission_classes = [IsAuthenticated]
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['lat']
        self.room_group_name = 'chat_%s' % self.room_name
        #######################################################
        # from channels.auth import AuthMiddlewareStack
        from django.db import close_old_connections
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from jwt import decode as jwt_decode
        from django.conf import settings
        # settings.configure()
        # from django.contrib.auth import get_user_model
        from accounts.models import User
        from urllib.parse import parse_qs

        # from asgiref.sync import sync_to_async
                # Get the token
        user_token = dict(self.scope['headers'])[b'token'].decode("utf8")
        self.scope["query_string"] = "token=" + user_token

        token = user_token

                # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            AccessToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(decoded_data)
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }

            # Get the user using ID

            user = User.objects.get(id=decoded_data["user_id"])
            self.scope['user'] = user

        # Return the inner application directly and let it run everything else
        # return await self.inner(scope, receive, send)


#################################
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
        # update_location(user, latitude, longitude)
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
