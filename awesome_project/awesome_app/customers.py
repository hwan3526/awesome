# # import json

# # from asgiref.sync import async_to_sync
# # from channels.generic.websocket import WebsocketConsumer


# # class ChatConsumer(WebsocketConsumer):
# #     def connect(self):
# #         """
# #         사용자와 WebSocket 연결이 맺어졌을 때 호출
# #         """
# #         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
# #         self.room_group_name = "chat_%s" % self.room_name

# #         # Join room group
# #         async_to_sync(self.channel_layer.group_add)(
# #             self.room_group_name, self.channel_name
# #         )

# #         self.accept()

# #     def disconnect(self, close_code):
# #         """
# #         사용자와 WebSocket 연결이 끊겼을 때 호출
# #         """
# #         # Leave room group
# #         async_to_sync(self.channel_layer.group_discard)(
# #             self.room_group_name, self.channel_name
# #         )

# #     # Receive message from WebSocket
# #     def receive(self, text_data):
# #         """
# #         사용자가 메세지를 보낼 떄 호출
# #         """
# #         text_data_json = json.loads(text_data)
# #         message = text_data_json["message"]

# #         # Send message to room group
# #         async_to_sync(self.channel_layer.group_send)(
# #             self.room_group_name, {"type": "chat_message", "message": message}
# #         )

# #     # Receive message from room group
# #     def chat_message(self, event):
# #         message = event["message"]

# #         # Send message to WebSocket
# #         self.send(text_data=json.dumps({"message": message}))

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import chat_messages
# from django.contrib.auth.models import User

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         username = text_data_json["username"]  # username을 추출

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {
#                 "type": "chat_message",
#                 "message": message,
#                 "username": username  # username을 함께 전송
#             }
#         )
        
        

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#         username = event["username"]  # username을 추출

#         # Send message and username to WebSocket
#         await self.send(text_data=json.dumps({
#             "message": message,
#             "username": username  # username도 함께 전송
#         }))
        

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import chat_messages, chat_room
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def get_room(self, room_number):
        return chat_room.objects.get(id=room_number)

    @database_sync_to_async
    def get_sender(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_chat_message(self, room, sender, message):
        chat_msg = chat_messages(chat_room=room, sender=sender, message=message, read_or_not=False)
        chat_msg.save()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        room_number = text_data_json["room_number"]
        created_at = text_data_json["created_at"]

        room = await self.get_room(room_number)
        sender = await self.get_sender(username)

        await self.save_chat_message(room, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat_message",
                "message": message,
                "username": username,
                "created_at": created_at,
                "room_number": room_number
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        created_at = event["created_at"]
        room_number = event["room_number"]

        # Send message and username to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "created_at": created_at,
            "room_number": room_number
        }))
