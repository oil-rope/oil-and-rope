from django.urls import include, path
from rest_framework import routers

from . import views, viewsets

router = routers.DefaultRouter()
router.register(r'chat', viewset=viewsets.ChatViewSet, basename='chat')


app_name = 'chat'

urlpatterns = [
    path('api/', include((router.urls, 'api'))),
    path('', views.BaseChatView.as_view(), name='main'),
]
