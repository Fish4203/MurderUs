from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    doneness = models.IntegerField()
    type = models.CharField(max_length=200)
    code = models.IntegerField()
    var1 = models.CharField(max_length=200)
    var2 = models.CharField(max_length=200)
    var3 = models.CharField(max_length=200)

class Player(models.Model):
    name = models.CharField(max_length=200)
    aliveness = models.IntegerField()
    tag = models.IntegerField()
    tasks = models.ManyToManyField(Task)
    role = models.CharField(max_length=200)

class Game(models.Model):
    gameId = models.IntegerField()
    meating = models.IntegerField()
    tasks = models.ManyToManyField(Task)
    players = models.ManyToManyField(Player)

    def __str__(self):
        return self.id
