from django.urls import include, path
from rest_framework.authtoken.views import ObtainAuthToken

from . import views
from .routers import chat, dynamic_menu, registration, roleplay

app_name = 'api'

urlpatterns = [
    path('', views.ApiVersionView.as_view(), name='version'),
    path('token/', ObtainAuthToken.as_view(), name='token'),
    path('registration/', include((registration.urls, 'registration'))),
    path('chat/', include((chat.urls, 'chat'))),
    path('dynamic_menu/', include((dynamic_menu.urls, 'dynamic_menu'))),
    path('roleplay/', include((roleplay.urls, 'roleplay'))),
]
