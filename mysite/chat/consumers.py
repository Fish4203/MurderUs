import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import *
import random
import operator


def imposterAsign(players, tasknum): # assigns all the players in the player list function with a rasndom set of bad tasks
    # tasks are defined here just add or remove from list to chang what tasks get chosen
    tasks = []
    tasks.append(Task(
        doneness=3,
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
        doneness=3,
        type='sabotage',
        name='disable fence',
        codefinal='tree',
        code1='12',
        code2='34',
        location1='controle',
        location2='tree',
        location3='fence'
        ))

    # assigns the role and tasks for eath player and then saves the player
    for player in players:
        player.role = 'imp'

        for i in range(tasknum):
            task = random.choice(tasks)
            task.save()

            player.tasks.add(task)

        player.save()


def rogeAssign(players, tasknum): # assigns all the players in the player list function with a rasndom set of roge tasks
# tasks are defined here just add or remove from list to chang what tasks get chosen
    tasks = []
    tasks.append(Task(
        doneness=3,
        type='good',
        name='minigame 1',
        codefinal='mini1',
        location1='power box',
        ))

    tasks.append(Task(
        doneness=3,
        type='good',
        name='enter codes',
        codefinal='1111',
        code1='1234',
        code2='5678',
        location1='controle',
        location2='tree',
        location3='fence'
        ))

    # assigns the role and tasks for eath player and then saves the player
    for player in players:
        player.role = 'roge'

        for i in range(tasknum):
            task = random.choice(tasks)
            task.save()

            player.tasks.add(task)

        player.save()


def inocentAssign(players, tasknum): # assigns all the players in the player list function with a rasndom set of good tasks
    # tasks are defined here just add or remove from list to chang what tasks get chosen
    tasks = []
    tasks.append(Task(
        doneness=1,
        type='good',
        name='minigame 1',
        codefinal='mini1',
        location1='power box',
        ))

    tasks.append(Task(
        doneness=3,
        type='good',
        name='enter codes',
        codefinal='1111',
        code1='1234',
        code2='5678',
        location1='controle',
        location2='tree',
        location3='fence'
        ))

    # assigns the role and tasks for eath player and then saves the player
    for player in players:
        player.role = 'in'

        for i in range(tasknum):
            task = random.choice(tasks)
            task.save()

            player.tasks.add(task)

        player.save()



# this is the big kahona the big boy class that defines how the database interacts with the websocket and how the websocket interacts with the users
class ChatConsumer(AsyncWebsocketConsumer):

    ### async functions interact with the user and the web sockets while but cant interact with a database
    async def connect(self): # called when a user first connects to the server
        # gets some names of the room
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code): # called when a websocket disconnects
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data): # Receive message from WebSocket heres where the magice happens heres where the real code is writen
        text_data_json = json.loads(text_data) # loads the data sent over by the user

        if text_data_json['role'] == 'initial': # when a user first connects this is called
            # new player
            await database_sync_to_async(self.newPlayer)(text_data_json)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'players',
                }
            ) # sends a message to all users about the new player

        elif text_data_json['role'] == 'start': # called when the game starts
            # the game starts
            await database_sync_to_async(self.startGame)(text_data_json)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'start',
                }
            )# sends a message to all users about the start of the game

        elif text_data_json['role'] == 'meating': # called when a meating is called
            # a meating is called
            await database_sync_to_async(self.meating)(text_data_json)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'meating',
                }
            ) # sends a message to all users about the meating

        elif text_data_json['role'] == 'taskcode':
            # a task code is submited
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'taskcode',
                    'result': await database_sync_to_async(self.tasksubmit)(text_data_json)
                }
            ) # sends a message to all users about the task code


        elif text_data_json['role'] == 'vote': # called when a user votes in a meating
            # a vote is cast
            await database_sync_to_async(self.vote)(text_data_json)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message',
                    'role': 'voted',
                    'user': text_data_json['user'],
                }
            ) # sends a message to all users that user has voted

        elif text_data_json['role'] == 'kill': # called when some one dies
            # kill a human

            await self.send(text_data=json.dumps({
                'role': 'kill',
                'result': await database_sync_to_async(self.kill)(text_data_json)
            })) # sends a mesage to the killer wether or not they have killed the person


        elif text_data_json['role'] == 'getInfo': # called when a user wants info about the game
            # sends game info to given user
            await self.send(text_data=json.dumps({
                'role': 'gameInfo',
                'gameInfo': await database_sync_to_async(self.gameInfo)(text_data_json),
                'playerInfo': await database_sync_to_async(self.playerInfo)(text_data_json)
            })) # sends the info about the game to the user who requested it



    # Receive message from room group
    async def message(self, event): # when a message needs to be sent the the whole room this function passes it on
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))


    ### regular function can talk to the database but not he web socket or the users
    def startGame(self, text_data_json): # called when the game starts
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object


        imposterAsign([random.choice(game.players.filter(role='na')) for i in range(int(text_data_json['impnum']))], int(text_data_json['tasknum']))
        rogeAssign([random.choice(game.players.filter(role='na')) for i in range(int(text_data_json['rogenum']))], int(text_data_json['tasknum']))
        inocentAssign(game.players.filter(role='na'), int(text_data_json['tasknum']))

        for player in game.players.all():
            for task in player.tasks.all():
                game.tasks.add(task)

        game.status = 'running'
        game.save()


    def meating(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object

        game.status = 'meating'
        game.save()

    def vote(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object
        player = game.players.get(name=text_data_json['user'])
        person = game.players.get(name=text_data_json['person'])



        if game.status == 'meating' and player.voted == 0 and player.aliveness == 1:
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

                    for task in elimenated.tasks.all():
                        task.delete()
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



    def kill(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object
        player = game.players.get(name=text_data_json['user'])
        victem = game.players.filter(tag=text_data_json['tag'])

        if len(victem) == 1 and player.aliveness == 1:
            victem[0].aliveness = 0
            victem[0].save()

            for task in victem[0].tasks.all():
                task.delete()



            return 1
        return 0

    def tasksubmit(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0]
        player = game.players.get(name=text_data_json['user'])
        task = game.tasks.get(id=text_data_json['taskid'])

        if player.aliveness == 1:

            if text_data_json['code'] == task.codefinal:
                task.doneness = 0
            elif text_data_json['code'] == task.code1:
                task.doneness = 1
            elif text_data_json['code'] == task.code2:
                task.doneness = 2
        else:
            return 0

        task.save()
        game.save()
        return 1

    def playerInfo(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object
        player = game.players.filter(name=text_data_json['user'])

        if len(player) != 0:
            player = player[0]

            tasks = [{
                'doneness': task.doneness,
                'type': task.type,
                'name': task.name,
                'id': task.id,
                'location': [task.location1, task.location2, task.location3],
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
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object

        if len(game.tasks.all()) != 0:
            taskProgres = len(game.tasks.filter(doneness=0)) / len(game.tasks.all()) * 100
        else:
            taskProgres = 0

        out = {
            'status': game.status,
            'taskProgres': taskProgres,
            'players': [player.name for player in game.players.all()]
        }
        return out


    def newPlayer(self, text_data_json):
        game = Game.objects.filter(gameId=text_data_json['gameID'])[0] # get the game object
        player = game.players.filter(name=text_data_json['user'])

        if len(player) == 0:
            player = Player(name=text_data_json['user'], aliveness=1, tag=0, role='na', votes=0, voted=0)
            player.save()
            player.tag = (int(player.id) * int(text_data_json['gameID'])) % 10000
            player.save()
        else:
            player = player[0]

        game.players.add(player)
        game.save()
