import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User, Chat, Message
#import sync_to_async
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['chat_name']
        # check if user is in chat
        # define a user for each channel
        self.user = self.scope['user']
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
        message = text_data_json['message']
        user = self.user
        chat = await database_sync_to_async(
            Chat.objects.filter)(name=self.room_group_name)
        # await database_sync_to_async(print)(await database_sync_to_async(chat.exists)(), self.room_group_name)
        # check if chat exists asynchronusly
        if await database_sync_to_async(chat.exists)():
            chat = await database_sync_to_async(chat.first)()
            all_users = await database_sync_to_async(chat.users.all)()
            # create a lambda function to check if user is in chat
            def check_user(user): return user in all_users
            user_in_chat = await database_sync_to_async(check_user)(user)
            if user_in_chat:
                message = await database_sync_to_async(Message)(sender=user, chat=chat, body=message)
                await database_sync_to_async(message.save)()
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message.body,
                        'user': user.username
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'error': 'You are not in this chat.'
                }))
        else:
            await self.send(text_data=json.dumps({
                'error': 'Chat does not exist.'
            }))
    # Receive message from room group

    async def chat_message(self, event):
        message = event['message']
        username = event['user']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
