import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import *
import random
import operator

def sabotageTask():
    tasks = []
    tasks.append(Task(
        doneness=0,
        type='sabotage',
        name='sabotage power',
        codefinal='fish',
        code1='12',
        code2='34',
        location1='power box',
        location2='eletric',
        location3='controle'
        ))

    tasks.append(Task(
        doneness=0,
        type='sabotage',
        name='disable fence',
        codefinal='tree',
        code1='12',
        code2='34',
        location1='controle',
        location2='tree',
        location3='fence'
        ))

    return random.choice(tasks)

def goodTask():
    tasks = []
    tasks.append(Task(
        doneness=0,
        type='good',
        name='minigame 1',
        codefinal='mini1',
        location1='power box',
        ))

    tasks.append(Task(
        doneness=0,
        type='good',
        name='enter codes',
        codefinal='1111',
        code1='1234',
        code2='5678',
        location1='controle',
        location2='tree',
        location3='fence'
        ))

    return random.choice(tasks)


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
            await database_sync_to_async(self.newPlayer)(text_data_json)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'players',
                }
            )
        elif text_data_json['role'] == 'start':
            # the game starts
            await database_sync_to_async(self.startGame)(text_data_json)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'start',
                }
            )

        elif text_data_json['role'] == 'meating':
            # a meating is called
            await database_sync_to_async(self.meating)(text_data_json)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'meating',
                }
            )

        elif text_data_json['role'] == 'submitTask':
            # a meating is called
            await self.send(text_data=json.dumps({
                'role': 'taskResult',
                'result': await database_sync_to_async(self.submitTask)(text_data_json)
            }))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'taskSubmited',
                }
            )

        elif text_data_json['role'] == 'vote':
            # a vote is cast
            await database_sync_to_async(self.vote)(text_data_json)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'voted',
                    'user': text_data_json['user'],
                }
            )

        elif text_data_json['role'] == 'kill':
            # kill a human

            await self.send(text_data=json.dumps({
                'role': 'kill',
                'result': await database_sync_to_async(self.kill)(text_data_json)
            }))


        elif text_data_json['role'] == 'gameInfo':
            # sends game info to given user
            await self.send(text_data=json.dumps({
                'role': 'gameInfo',
                'gameInfo': await database_sync_to_async(self.gameInfo)(text_data_json)
            }))

        elif text_data_json['role'] == 'playerInfo':
            # sends player info to given user
            await self.send(text_data=json.dumps({
                'role': 'playerInfo',
                'playerInfo': await database_sync_to_async(self.playerInfo)(text_data_json)
            }))




    # Receive message from room group
    async def message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    def meating(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]

        game.status = 'meating'
        game.save()

    def vote(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        player = game.players.get(name=text_data_json['user'])
        person = game.players.get(name=text_data_json['person'])



        if game.status == 'meating' and player.voted == 0:
            if text_data_json['person'] == text_data_json['user']:
                player.votes += 1
                player.voted = 1
                player.save()
            else:
                person.votes += 1
                player.voted = 1

                player.save()
                person.save()

            game.save()

            if len(game.players.filter(aliveness=1).filter(voted=0)) == 0:
                elimenated = game.players.filter(aliveness=1).order_by('votes')[len(game.players.filter(aliveness=1)) - 1]

                try:
                    elimenated.aliveness = 0
                    elimenated.save()
                except:
                    pass

                for playe in game.players.all():
                    playe.voted = 0
                    playe.votes = 0
                    playe.save()

                game.status = 'running'
                game.save()
                return 1

            return 0


    def startGame(self, text_data_json, tasknum=2, numimp=1,):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        for i in range(numimp):
            bp = random.choice(game.players.all())
            bp.role = 'imp'

            for i in range(tasknum):
                task = sabotageTask()
                task.save()

                bp.tasks.add(task)
                game.tasks.add(task)

            bp.save()


        for gp in game.players.filter(role='in'):
            for i in range(tasknum):
                task = goodTask()
                task.save()

                gp.tasks.add(task)
                game.tasks.add(task)

            gp.save()

        game.status = 'running'
        game.save()


    def submitTask(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        task = game.tasks.get(id=text_data_json['taskID'])

        if task.codefinal == text_data_json['code']:
            task.doneness = 1
            task.save()
            return 2
        elif task.code1 == text_data_json['code']:
            task.code1 = ''
            task.save()
            return 1
        elif task.code2 == text_data_json['code']:
            task.code2 = ''
            task.save()
            return 1
        else:
            return 0


    def kill(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        victem = game.players.filter(name=text_data_json['victem']).filter(tag=text_data_json['tag'])

        if len(victem) == 1:
            victem[0].aliveness = 0
            victem[0].save()

            return 1
        return 0


    def playerInfo(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        player = game.players.filter(name=text_data_json['user'])

        if len(player) != 0:
            player = player[0]

            tasks = [{
                'doneness': task.doneness,
                'type': task.type,
                'name': task.name,
                'id': task.id,
                'location1': task.location1,
                'location2': task.location2,
                'location3': task.location3
            } for task in player.tasks.all()]

            out = {
                'name': player.name,
                'aliveness': player.aliveness,
                'tag': player.tag,
                'role': player.role,
                'tasks': tasks,
                'votes': player.votes,
                'voted': player.voted
            }

        return out


    def gameInfo(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]

        if len(game.tasks.all()) != 0:
            taskProgres = len(game.tasks.filter(doneness=1)) / len(game.tasks.all())
        else:
            taskProgres = 0

        out = {
            'status': game.status,
            'taskProgres': taskProgres,
            'players': [player.name for player in game.players.all()]
        }
        return out


    def newPlayer(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        player = game.players.filter(name=text_data_json['user'])

        if len(player) == 0:
            player = Player(name=text_data_json['user'], aliveness=1, tag=random.randint(0,2000), role='in', votes=0, voted=0)
            player.save()
        else:
            player = player[0]

        game.players.add(player)
        game.save()
