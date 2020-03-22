from django.urls import path

from . import consumers

urlpatterns = [
    path('bot/', consumers.BotConsumer, name='bot_consumer')
]
