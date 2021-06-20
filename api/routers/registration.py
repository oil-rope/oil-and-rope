from rest_framework.routers import DefaultRouter

from .routers import OilAndRopeDefaultRouter

from ..viewsets.registration import ProfileViewSet, UserViewSet

router = OilAndRopeDefaultRouter()
router.register(r'user', UserViewSet, 'user')
router.register(r'profile', ProfileViewSet, 'profile')
