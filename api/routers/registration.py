from rest_framework import routers

from ..viewsets.registration import UserViewSet, ProfileViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet, 'user')
router.register(r'profile', ProfileViewSet, 'profile')
