from rest_framework.routers import SimpleRouter

from ..viewsets.chat import ChatMessageViewSet, ChatViewSet

router = SimpleRouter()
router.register(prefix='', viewset=ChatViewSet, basename='chat')
router.register(prefix=r'message', viewset=ChatMessageViewSet, basename='message')

urls = router.urls
