from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    # Task model
    # core info
    doneness = models.IntegerField() # one for done 0 for not done
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    note = models.CharField(max_length=500)
    # codes foe each stage of the task
    codefinal = models.CharField(max_length=200, default='', blank=True)
    code1 = models.CharField(max_length=200, default='', blank=True)
    code2 = models.CharField(max_length=200, default='', blank=True)
    # locations of each stage
    location1 = models.CharField(max_length=200, default='', blank=True)
    location2 = models.CharField(max_length=200, default='', blank=True)
    location3 = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    # player in a game
    name = models.CharField(max_length=200) # this is the same as the user name
    aliveness = models.IntegerField() # 1 for alove 0 for dead
    tag = models.IntegerField() # a random code needed to kill someone
    tasks = models.ManyToManyField(Task)
    role = models.CharField(max_length=200) # what role the user is default is un
    votes = models.IntegerField() # how many votes they have recieved in a meating
    voted = models.IntegerField() # wether or not they have voted

    def __str__(self):
        return self.name

class Game(models.Model):
    # a game
    gameId = models.IntegerField() # the noom number
    status = models.CharField(max_length=200) # wat stage the game is in
    tasks = models.ManyToManyField(Task)
    players = models.ManyToManyField(Player)
    auth = models.CharField(max_length=200, default='', blank=True) # an optional auth code for authorised task compleation

    def __str__(self):
        return str(self.gameId)
