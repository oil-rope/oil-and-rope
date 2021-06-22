from django.apps import apps
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
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

    def create_by_admin(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def create_by_user(self, request, *args, **kwargs):
        user = kwargs['user']
        data = request.data.copy()
        data['author'] = user.pk

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create(self, request, *args, **kwargs):
        """
        Same behaviour as :class:`CreateModelMixin` but checking for admin and author in data.
        """

        user = request.user
        kwargs['user'] = user

        if user.is_authenticated and user.is_staff:
            return self.create_by_admin(request, *args, **kwargs)
        else:
            return self.create_by_user(request, *args, **kwargs)

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

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            qs = super().get_queryset()
        else:
            qs = super().get_queryset().filter(
                author_id=user.pk,
            )
        return qs
