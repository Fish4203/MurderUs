import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import *
import random

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
        tree = await database_sync_to_async(self.get_name)()

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
        if text_data_json['role'] == 'initial':
            # new player
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'players',
                    'players': await database_sync_to_async(self.newPlayer)(text_data_json),
                    'gameInfo': await database_sync_to_async(self.gameInfo)(text_data_json)
                }
            )
        elif text_data_json['role'] == 'start':
            # the game starts
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'start',
                    'gameInfo': await database_sync_to_async(self.gameInfo)(text_data_json, 'running')
                }
            )

        elif text_data_json['role'] == 'start':
            # starting the game
            pass
        elif text_data_json['role'] == 'meating':
            # a meating is called
            pass


    # Receive message from room group
    async def message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    def startGame(self, text_data_json, numimp=2):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]

        for i in range(numimp):
            bp = random.choice(game.players.all())
            bp.role = 'imp'

            bp.tasks.add(Tasks.objects.filter(type='bad'))

            bp.save()
        game.tasks.add(Tasks.objects.filter(type='bad'))

        gtasks = Tasks.objects.filter(type='good')

        for gp in game.players.filter(role='in'):
            gt = random.choice(gtasks)
            gp.tasks.add(gt)
            game.tasks.add(gt)

            gp.save()

        game.status = 'running'

        game.save()

    def kill(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        victem = game.players.filter(name=text_data_json['victemName']).filter(tag=text_data_json['victemTag'])

        if len(victem) == 1:
            victem.aliveness = 0
            victem.save() 



    def gameInfo(self, text_data_json, status=''):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]

        if len(game.tasks.all()) != 0:
            taskProgres = len(game.tasks.filter(doneness==1)) / len(game.tasks.all())
        else:
            taskProgres = 0

        out = {
            'status': game.status,
            'taskProgres': taskProgres
        }
        return out


    def newPlayer(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        player = game.players.filter(name=text_data_json['user'])

        if len(player) == 0:
            player = Player(name=text_data_json['user'], aliveness=1, tag=random.randint(0,2000), role='in')
            player.save()
        else:
            player = player[0]

        game.players.add(player)
        game.save()

        out = []
        for user in game.players.all():
            out.append(user.name)
        return out
