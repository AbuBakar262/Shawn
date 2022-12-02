# from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from channels.db import database_sync_to_async



# from django.conf import settings
# settings.configure()
# from django.contrib.auth import get_user_model

# from urllib.parse import parse_qs



# from asgiref.sync import sync_to_async

class TokenAuthMiddleware:
    """
    Custom token auth middleware
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    # @sync_to_async
    async def __call__(self, scope, receive, send):

        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Get the token
        user_token = dict(scope['headers'])[b'token'].decode("utf8")
        scope["query_string"] = "token="+user_token


        token = user_token

        # Try to authenticate the user
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from jwt import decode as jwt_decode
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            # This will automatically validate the token and raise an error if token is invalid
            AccessToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            from accounts.models import User
            from sean_backend import settings
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
            scope['user'] = user

        # Return the inner application directly and let it run everything else
        return await self.inner(scope, receive, send)
