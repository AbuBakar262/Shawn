from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/livetracking/(?P<lat>\w+)/$', consumers.LiveTrackingConsumer.as_asgi()),
]
