import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import *

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'help me pls',
            'user': 'self.user'
        }))

    def get_name(self):
        out = []
        for user in User.objects.all():
            out.append(user.username)
        return out



    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['role'] == 'new':
            # new player
            print(text_data_json['user'], text_data_json.keys())
            #game = Game.objects.filter(gameId=text_data_json['gameID'])

            #if len(game) == 0:
            #    print('worked')

        message = text_data_json['message']
        user = text_data_json['user']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        if event['role'] == 'new':
            print('new', event['user'], dir(event))
        else:
            message = event['message']
            user = event['user']
            print('no')

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'user': user
            }))
