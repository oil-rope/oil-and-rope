from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models import Channel
from common.constants.models import CHAT, REGISTRATION_USER
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
    discord_id: Optional[:class:`str`]
        Discord chat associated if given.
    """

    id = models.BigAutoField(primary_key=True, verbose_name=_('identifier'))
    name = models.CharField(verbose_name=_('name'), max_length=254)
    users = models.ManyToManyField(to=REGISTRATION_USER, verbose_name=_('users'), related_name='chat_set')
    discord_id = models.CharField(
        verbose_name=_('discord identifier'), max_length=100, null=False, blank=True, db_index=True,
    )

    @property
    def discord_chat(self):
        if not self.discord_id:
            return None
        d_chat = Channel(self.discord_id)
        return d_chat

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
        to=CHAT, verbose_name=_('chat'), on_delete=models.CASCADE, related_name='chat_message_set',
        db_index=True,
    )
    message = models.CharField(verbose_name=_('message'), max_length=150, null=False, blank=False)
    author = models.ForeignKey(
        to=REGISTRATION_USER, verbose_name=_('author'), on_delete=models.CASCADE, related_name='chat_message_set',
        db_index=True,
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')

    def __str__(self):
        return f'{self.message} ({self.entry_created_at})'
