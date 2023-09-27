from django.urls import re_path

from . import customers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\d+)/$", customers.ChatConsumer.as_asgi()),
]

