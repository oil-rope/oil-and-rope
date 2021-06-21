from ..viewsets.registration import ProfileViewSet, UserViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'user', viewset=UserViewSet, basename='user')
router.register(prefix=r'profile', viewset=ProfileViewSet, basename='profile')
