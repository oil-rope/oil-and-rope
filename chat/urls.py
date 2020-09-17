from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()


app_name = 'chat'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.BaseChatView.as_view(), name='main'),
]
