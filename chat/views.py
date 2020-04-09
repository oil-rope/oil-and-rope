from django.shortcuts import render
from django.views.generic import TemplateView


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


def index(request):
    return render(request, 'chat/room_index.html')


class roomView(templateView):
    """
    Chat rooms View
    """

    template_name = "chat/room_index.html"
