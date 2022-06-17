from django.apps import apps
from django.contrib.auth import get_user_model
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

    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().filter(
            users__in=[user],
        )
        return qs

    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=True, url_name='detail-nested', url_path='nested')
    def retrieve_nested(self, request: Request, *args, **kwargs):
        """
        Retrieve chat with messages as objects instead of IDs.
        """

        self.serializer_class = NestedChatSerializer
        return self.retrieve(request, *args, **kwargs)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for :class:`~chat.models.ChatMessage`.
    """

    queryset = ChatMessage.objects.all()
    serializer_class = NestedChatMessageSerializer

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().filter(
            author=user,
        )
        return qs

    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request: Request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request: Request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.serializer_class = ChatMessageSerializer
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Regular user should not be able to set other author than themselves
        return serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        self.serializer_class = ChatMessageSerializer
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Regular user should not be able to change chat
        return serializer.save(chat=instance.chat)
