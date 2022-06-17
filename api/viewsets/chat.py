from django.apps import apps
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request

from common.constants import models

from ..serializers.chat import ChatMessageSerializer, ChatSerializer, NestedChatMessageSerializer, NestedChatSerializer

Chat = apps.get_model(models.CHAT)
ChatMessage = apps.get_model(models.CHAT_MESSAGE)
User = get_user_model()


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`~chat.models.Chat`.
    """

    queryset = None
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Chat.objects.filter(
            users__in=[user],
        )
        if not user.is_staff:
            return qs
        if self.action == 'list':
            return qs
        return Chat.objects.all()

    @swagger_auto_schema(tags=['chat'])
    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['chat'])
    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['chat'])
    @action(methods=['get'], detail=False, url_path='all', permission_classes=[IsAdminUser])
    def list_all(self, request: Request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['chat'])
    @action(methods=['get'], detail=True, url_name='detail-nested', url_path='nested')
    def nested_retrieve(self, request: Request, *args, **kwargs):
        self.serializer_class = NestedChatSerializer
        return self.retrieve(request, *args, **kwargs)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for :class:`~chat.models.ChatMessage`.
    """

    queryset = None
    serializer_class = NestedChatMessageSerializer

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = ChatMessage.objects.filter(
            author=user,
        )
        if not user.is_staff:
            return qs
        if self.action == 'list':
            return qs
        return ChatMessage.objects.all()

    def create(self, request, *args, **kwargs):
        self.serializer_class = ChatMessageSerializer
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            return serializer.save()
        # Regular user should not be able to set other author than themself
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            return serializer.save()
        instance = self.get_object()
        # Regular user should not be able to change chat
        return serializer.save(chat=instance.chat)

    def update(self, request, *args, **kwargs):
        self.serializer_class = ChatMessageSerializer
        return super().update(request, *args, **kwargs)

    @action(methods=['get'], detail=False, url_path='all', permission_classes=[IsAdminUser])
    def list_all(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
