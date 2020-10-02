from django.shortcuts import render

# Create your views here.


def index(request):
    context = {"additional_context": {'a': 'chat'}}
    return render(request, 'chat/index.html', context)

def room(request, room_name):
    context = {"additional_context": {'a': 'chat'}, 'room_name': room_name}
    return render(request, 'chat/room.html', context)
