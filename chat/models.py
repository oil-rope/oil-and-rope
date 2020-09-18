from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Chat(models.Model):
    """
    In-game chat model

    Parameters
    ----------
    name: :class:`str`
    users: :class:`User`
    private_game: :class:`??????`
        The private game the users are playing (not like pathfinder)
    game: :class:`Game`
        Like pathfinder, dnd...
    """

    name = models.CharField(verbose_name=_('Chat name'), max_length=50)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('Users'),
                                   related_name='chat_set')

    class Meta:
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')

    def __str__(self):
        return f'{self.name} ({self.pk})'


class ChatMessage(models.Model):
    """
    Ingame chat messages.

    Parameters
    ----------
    chat: :class:`Chat`
    message: :class:`str`
    user: :class:`User`
    """

    chat = models.ForeignKey('chat.Chat', verbose_name=_('Chat'),
                             on_delete=models.CASCADE, related_name='chat_message_set')
    message = models.CharField(verbose_name=_('Message'), max_length=150)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'),
                               on_delete=models.CASCADE, related_name='chat_message_set')
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        verbose_name=_('Entry created at'),
    )

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')

    def __str__(self):
        return self.message

    def get_absolute_url(self):
        return reverse('chatmessage_detail', kwargs={'pk': self.pk})
