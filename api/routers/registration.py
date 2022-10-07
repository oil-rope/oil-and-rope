from django.urls import path

from ..viewsets.registration import BotViewSet, UserViewSet

urls = [
    path('user/', UserViewSet.as_view(), name='user'),
    path('bot/', BotViewSet.as_view(), name='bot'),
]
