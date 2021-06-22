from django.apps import apps
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from common.constants import models

from ..serializers.chat import ChatMessageSerializer, ChatSerializer

Chat = apps.get_model(models.CHAT_MODEL)
ChatMessage = apps.get_model(models.CHAT_MESSAGE_MODEL)
User = apps.get_model(models.USER_MODEL)


class ChatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for :class:`Chat`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            qs = super().get_queryset()
        else:
            qs = super().get_queryset().filter(
                users__in=[user],
            )
        return qs


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for :class:`ChatMessage`.
    """

    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            qs = super().get_queryset()
        else:
            qs = super().get_queryset().filter(
                author_id=user.pk,
            )
        return qs

    def perform_create(self, serializer):
        self._check_user_in_chat(serializer.validated_data)
        super().perform_create(serializer)

    # noinspection PyMethodMayBeStatic
    def _check_user_in_chat(self, data):
        user = data['author']
        chat = data['chat']

        if user not in chat.users.all():
            msg = _('User not in chat')
            raise ValidationError({'author': f'{msg}.'})

    def get_serializer(self, *args, **kwargs):
        if 'data' not in kwargs:
            return super().get_serializer(*args, **kwargs)

        user = self.request.user
        data = kwargs['data'].copy()

        if user.is_authenticated and not user.is_staff:
            if self.request.method.lower() == 'post':  # For create author is not needed
                data['author'] = user.pk
            if self.request.method.lower() == 'put':  # For update just message is needed
                data['author'] = user.pk
                data['chat'] = self.get_object().chat.pk

        kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)
