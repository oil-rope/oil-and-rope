from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TracingMixin


class Chat(TracingMixin):
    """
    In-game chat model

    Parameters
    ----------
    name: :class:`str`
        Name of the Chat Room.
    users: List[:class:`User`]
        Users in this chat.
    """

    name = models.CharField(verbose_name=_('Chat name'), max_length=50)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Users'),
                                   related_name='chat_set')

    class Meta:
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')

    def __str__(self):
        return f'{self.name} ({self.pk})'


class ChatMessage(TracingMixin):
    """
    Ingame chat messages.

    Parameters
    ----------
    chat: :class:`Chat`
        Chat associated to this message.
    message: :class:`str`
        Message itself.
    author: :class:`User`
        Person who sent the message.
    """

    chat = models.ForeignKey('chat.Chat', verbose_name=_('Chat'),
                             on_delete=models.CASCADE, related_name='chat_message_set')
    message = models.CharField(verbose_name=_('Message'), max_length=150)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'),
                               on_delete=models.CASCADE, related_name='chat_message_set')

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')

    def __str__(self):
        return f'{self.message} ({self.entry_created_at})'
