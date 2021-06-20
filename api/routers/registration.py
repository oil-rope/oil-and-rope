from ..viewsets.registration import ProfileViewSet, UserViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(r'user', UserViewSet, 'user')
router.register(r'profile', ProfileViewSet, 'profile')
