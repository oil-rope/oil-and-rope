from ..viewsets.chat import ChatMessageViewSet, ChatViewSet
from .routers import OilAndRopeDefaultRouter

router = OilAndRopeDefaultRouter()
router.register(prefix=r'chat', viewset=ChatViewSet, basename='chat')
router.register(prefix=r'message', viewset=ChatMessageViewSet, basename='message')
