from django.urls import include, path

from . import views
from .routers import chat, registration

app_name = 'api'

urlpatterns = [
    path('', views.ApiVersionView.as_view(), name='version'),
    path('registration/', include((registration.router.urls, 'registration'))),
    path('chat/', include((chat.router.urls, 'chat'))),
]
