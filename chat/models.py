from django.db import models
from django.utils.translation import gettext_lazy as _

from common.constants.models import CHAT_MODEL, USER_MODEL
from core.models import TracingMixin


class Chat(TracingMixin):
    """
    In-game chat model

    Parameters
    ----------
    name: :class:`str`
        Name of the Chat Room.
    users: List[:class:`~registration.models.User`]
        Users in this chat.
    """

    id = models.BigAutoField(primary_key=True, verbose_name=_('identifier'))
    name = models.CharField(verbose_name=_('name'), max_length=50)
    users = models.ManyToManyField(to=USER_MODEL, verbose_name=_('users'), related_name='chat_set')

    class Meta:
        verbose_name = _('chat')
        verbose_name_plural = _('chats')

    def __str__(self):
        return f'{self.name} ({self.pk})'


class ChatMessage(TracingMixin):
    """
    In-game chat messages.

    Parameters
    ----------
    chat: :class:`~chat.models.Chat`
        Chat associated to this message.
    message: :class:`str`
        Message itself.
    author: :class:`~registration.models.User`
        Person who sent the message.
    """

    id = models.BigAutoField(primary_key=True, verbose_name=_('identifier'))
    chat = models.ForeignKey(
        to=CHAT_MODEL, verbose_name=_('chat'), on_delete=models.CASCADE, related_name='chat_message_set', db_index=True
    )
    message = models.CharField(verbose_name=_('message'), max_length=150, null=False, blank=False)
    author = models.ForeignKey(
        to=USER_MODEL, verbose_name=_('author'), on_delete=models.CASCADE, related_name='chat_message_set',
        db_index=True
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return f'{self.message} ({self.entry_created_at})'
