from django.urls import include, path
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'user', viewsets.UserViewSet)
router.register(r'profile', viewsets.ProfileViewSet)

app_name = 'registration'

urlpatterns = [
    path('api/', include(router.urls)),
]
