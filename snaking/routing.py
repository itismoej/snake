from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        'ws/play/(?P<room_name>[^/]*)',
        view=consumers.GameConsumer.as_asgi()
    ),
]
