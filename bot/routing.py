from django.urls import re_path, include

from . import consumers

BOT_PATTERNS = [
    re_path(r'register/$', consumers.BotConsumer, name='ws_bot_register')
]

urlpatterns = [
    re_path(r'^ws/', include(BOT_PATTERNS))
]
