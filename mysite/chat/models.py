from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    doneness = models.IntegerField()
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    codefinal = models.CharField(max_length=200, default='', blank=True)
    code1 = models.CharField(max_length=200, default='', blank=True)
    code2 = models.CharField(max_length=200, default='', blank=True)

    location1 = models.CharField(max_length=200, default='', blank=True)
    location2 = models.CharField(max_length=200, default='', blank=True)
    location3 = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=200)
    aliveness = models.IntegerField()
    tag = models.IntegerField()
    tasks = models.ManyToManyField(Task)
    role = models.CharField(max_length=200)
    votes = models.IntegerField()
    voted = models.IntegerField()

    def __str__(self):
        return self.name

class Game(models.Model):
    gameId = models.IntegerField()
    status = models.CharField(max_length=200)
    tasks = models.ManyToManyField(Task)
    players = models.ManyToManyField(Player)
    auth = models.CharField(max_length=200, default='', blank=True)

    def __str__(self):
        return str(self.gameId)
