from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .models import *
# Create your views here.


def index(request):
    context = {"additional_context": {'a': 'chat'}}
    return render(request, 'chat/index.html', context)

def room(request, room_name):
    start = 0
    if len(Game.objects.filter(gameId=room_name)) == 0:
        game = Game(gameId=room_name, status='lobby')
        game.save()
        start = 1

    context = {"additional_context": {'a': 'chat'}, 'room_name': room_name, 'start': start}
    return render(request, 'chat/room.html', context)

def getCode(request, level, id, auth=''):
    task = Task.objects.get(id=id)

    if Game.objects.filter(tasks__id=id)[0].auth == auth:
        if level == 'final':
            task.doneness = 1
            task.save()
            response = {'status': 1}
        elif level == '1':
            task.code1 = ''
            task.save()
            response = {'status': 1}
        elif level == '2':
            task.code2 = ''
            task.save()
            response = {'status': 1}
        else:
            response = {'status': 0}
    else:
        response = {'status': 0}

    return JsonResponse(data=response)


def signin(request):
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


def new_account(request):

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
