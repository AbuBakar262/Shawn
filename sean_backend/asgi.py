# """
# ASGI config for sean_backend project.
#
# It exposes the ASGI callable as a module-level variable named ``application``.
#
# For more information on this file, see
# https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
# """
#
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import location.routing
from channels.security.websocket import AllowedHostsOriginValidator
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sean_backend.settings')

# application = ProtocolTypeRouter(
#     {
#         # (http->django views is added by default)
#         "websocket": TokenAuthMiddleware(
#             URLRouter(location.routing.websocket_urlpatterns)
#         )
#     }
# )
# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": TokenAuthMiddleware(
#         URLRouter(
#             location.routing.websocket_urlpatterns
#         )
#     ),
# })


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                location.routing.websocket_urlpatterns
            )
        )
    ),
})