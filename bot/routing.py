from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r'register/', consumers.BotConnectionOnRegisterConsumer, name='ws_bot_register')
]
