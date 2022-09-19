from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from ..viewsets.chat import ChatMessageViewSet, ChatViewSet

router = SimpleRouter()
router.register(prefix='', viewset=ChatViewSet, basename='chat')

messages_router = NestedSimpleRouter(
    parent_router=router,
    parent_prefix='',
    lookup='chat',
)
messages_router.register(prefix=r'messages', viewset=ChatMessageViewSet, basename='chat-message')

urls = [
    *router.urls,
    *messages_router.urls,
]
