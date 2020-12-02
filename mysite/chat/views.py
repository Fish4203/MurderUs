from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import *
# Create your views here.


def index(request): # index
    context = {"additional_context": {'a': 'chat'}}
    return render(request, 'chat/index.html', context)

def room(request, room_name): # room view
    start = 0
    # if there isnt already a game with this room num a game will be created
    if len(Game.objects.filter(gameId=room_name)) == 0:
        game = Game(gameId=room_name, status='lobby')
        game.save()
        start = 1

    context = {"additional_context": {'a': 'chat'}, 'room_name': room_name, 'start': start}
    return render(request, 'chat/room.html', context)

def submitTask(request, taskid,  auth=''):
    # used by the tasks to submit a compleated task
    task = Task.objects.get(id=taskid)

    # checks if the right authorisation is used
    if Game.objects.filter(tasks__id=taskid)[0].auth == auth:
        # changes the level the task is on
        task.doneness -= 1
        task.save()
        response = {'status': 1}
    else:
        response = {'status': 0}

    return JsonResponse(data=response) # responds with wether or not the right codes have been entered

def getTask(request, location, tag, auth=''):
    # used to sign users in and give them thr right task
    try:
        tasks = Player.objects.filter(name=request.POST['username']).get(tag=request.POST['Tag']).tasks.all()
    except:
        return JsonResponse(data={'status': 'playerNA'})

    # find a task at this location
    if len(tasks.filter(location1=location).filter(doneness=1)) > 0:
        task = tasks.filter(location1=location).filter(doneness=1)[0]
    elif len(tasks.filter(location2=location).filter(doneness=2)) > 0:
        task = tasks.filter(location2=location).filter(doneness=2)[0]
    elif len(tasks.filter(location3=location).filter(doneness=3)) > 0:
        task = tasks.filter(location3=location).filter(doneness=3)[0]
    else:
        return JsonResponse(data={'status': 'locationNA'})

    response = {
        'status': 'sucsess',
        'taskid': task.id,
        'level': task.level
    }
    return JsonResponse(data=response) # responds with wether or not the right codes have been entered



def signin(request): # sign in function this shit is well writen so im not going to bother commenting
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('chat:index')
        else:
            context = {'error_message': 'could not authentecate account'}
            return render(request, 'chat/signin.html', context)

    elif request.method == 'GET':
        return render(request, 'chat/signin.html')


def new_account(request): # creates a new user function this shit is well writen so im not going to bother commenting

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.save()

            context = 'sucsessfuly created new account'
            return redirect('chat:index', error=context)
        except:
            context = {'error_message': 'could not created new account'}
            return render(request, 'chat/new_account.html', context)

    elif request.method == 'GET':
        return render(request, 'chat/new_account.html')


def signout(request):
    logout(request)
    return redirect('chat:index')
