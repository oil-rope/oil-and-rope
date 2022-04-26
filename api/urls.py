from django.urls import include, path
from rest_framework.authtoken.views import ObtainAuthToken

from . import views
from .routers import chat, registration, roleplay

app_name = 'api'

UTILS_PATTERNS = [
    path('resolver/', views.URLResolverView.as_view(), name='resolver'),
    path('roll/', views.RollView.as_view(), name='roll_dice'),
]

AUTH_PATTERNS = [
    path('token/', ObtainAuthToken.as_view(), name='token'),
]

urlpatterns = [
    path('', views.ApiVersionView.as_view(), name='version'),
    path('auth/', include((AUTH_PATTERNS, 'auth'))),
    path('utils/', include((UTILS_PATTERNS, 'utils'))),
    path('registration/', include((registration.urls, 'registration'))),
    path('chat/', include((chat.urls, 'chat'))),
    path('roleplay/', include((roleplay.urls, 'roleplay'))),
]
