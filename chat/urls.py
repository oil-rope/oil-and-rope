from django.urls import include, path
from rest_framework import routers

from . import viewsets, views

app_name = 'chat'

router = routers.DefaultRouter()
router.register(r'chat', viewset=viewsets.ChatViewSet, basename='chat')

urlpatterns = [
    path('api/', include((router.urls, 'api'))),
    path('', views.ChatView.as_view(), name='index'),
]
