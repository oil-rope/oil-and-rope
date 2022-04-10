from ..viewsets.registration import BotViewSet, ProfileViewSet, UserViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'user', viewset=UserViewSet, basename='user')
router.register(prefix=r'profile', viewset=ProfileViewSet, basename='profile')
router.register(prefix=r'bot', viewset=BotViewSet, basename='bot')

urls = router.urls
