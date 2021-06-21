from ..viewsets.chat import ChatViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'chat', viewset=ChatViewSet, basename='chat')
