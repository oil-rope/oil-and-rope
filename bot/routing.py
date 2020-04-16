from django.urls import re_path

from . import consumers

app_name = 'bot_ws'

urlpatterns = [
    re_path(r'register/$', consumers.BotConsumer, name='register')
]
