from django.urls import re_path

from . import consumers

urlpatterns = [
    re_path(r'ws/register/$', consumers.BotConsumer, name='ws_bot_register')
]
