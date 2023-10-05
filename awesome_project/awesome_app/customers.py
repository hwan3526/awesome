import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import chat_messages, chat_room
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .views import autocomplete

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_number"]
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
    def save_chat_message(self, room, sender, message, receiver, chat_uuid):
        chat_msg = chat_messages(chat_room=room, sender=sender, message=message, read_or_not=False, receiver=receiver, chat_uuid=chat_uuid)
        chat_msg.save()

    @database_sync_to_async
    def get_chat_message_and_read_check(self, chat_uuid, receiver):
        try:
            chat_msg = chat_messages.objects.get(chat_uuid=chat_uuid, receiver=receiver)
            chat_msg.read_or_not = True
            chat_msg.save()
        except chat_messages.DoesNotExist:
            pass

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'chat_message':
            message = text_data_json["message"]
            username = text_data_json["username"]
            receiver_username = text_data_json["receiver"]
            room_number = text_data_json["room_number"]
            created_at = text_data_json["created_at"]
            chat_uuid = text_data_json["chat_uuid"]

            room = await self.get_room(room_number)
            sender = await self.get_sender(username)
            receiver = await self.get_sender(receiver_username)

            await self.save_chat_message(room, sender, message, receiver, chat_uuid)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat_message",
                    "message": message,
                    "username": username,
                    "created_at": created_at,
                    "room_number": room_number,
                    'chat_uuid': chat_uuid,
                    'receiver': receiver_username
                }
            )

        if text_data_json['type'] == 'chat_message_read':
            receiver = text_data_json["receiver"]
            room_number = text_data_json["room_number"]
            chat_uuid = text_data_json["chat_uuid"]

            receive_user = await self.get_sender(receiver)

            await self.get_chat_message_and_read_check(chat_uuid, receive_user)

            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat_message_read",
                    "chat_uuid": chat_uuid,
                    'room_number': room_number,
                    "receiver": receiver,
                    'is_read': True
                }
            )

        if text_data_json['type'] == 'chat_bot':
            message = text_data_json['message']
            created_at = text_data_json["created_at"]

            response_generator = autocomplete(message)
            for response in response_generator:
                try:
                    response_str = response.decode('utf-8')
                    response_data = json.loads(response_str)
                    message_content = response_data['message']
                    
                    await self.channel_layer.group_send(
                        self.room_group_name, {
                            "type": "chat_bot_send",
                            "message": message_content,
                            'created_at': created_at
                        }
                    )
                except Exception as e:
                    print(e)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        created_at = event["created_at"]
        room_number = event["room_number"]
        chat_uuid = event["chat_uuid"]

        # Send message and username to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            "message": message,
            "username": username,
            "created_at": created_at,
            "room_number": room_number, 
            'chat_uuid': chat_uuid
        }))
    
    async def chat_message_read(self, event):
        # 상대방에게 읽음 여부를 알리는 코드
        await self.send(text_data=json.dumps({
            'type': 'chat_message_read',
            "chat_uuid": event["chat_uuid"],
            'room_number': event['room_number'],
            "receiver": event["receiver"],
            "is_read": True
        }))

    async def chat_bot_send(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_bot_send',
            'message': event['message'],
            'created_at': event['created_at']
        }))
