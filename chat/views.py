from django.shortcuts import render
from django.views.generic import TemplateView


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


def index(request):
    return render(request, 'chat/room_index.html')
