from django.urls import include, path
from rest_framework import routers

from .viewsets import ChatMessageViewSet, ChatViewSet
from .views import room, index

router = routers.DefaultRouter()
router.register(r'chat', ChatViewSet)
router.register(r'chat_message', ChatMessageViewSet)


app_name = "chat"

urlpatterns = [
    path('api/', include(router.urls)),
    path('<str:room_name>/', room, name='room'),
    path('', index, name='index'),
]
