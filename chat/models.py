from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _


class Chat(models.Model):
    """
    In-game chat model

    Parameters
    ----------
    name: :class:`str`
    users: :class:`User`
    TODO:
    game: :class:`Game`
        Like pathfinder, dnd...
    board: :class:`Board`
        The private game
    """

    name = models.CharField(_("Chat name"), max_length=50)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=_("Usuarios"), related_name='chats')

    class Meta:
        verbose_name = _("Chat")
        verbose_name_plural = _("Chats")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Chat_detail", kwargs={"pk": self.pk})


class ChatMessage(models.Model):
    """
    Ingame chat messages.

    Parameters
    ----------
    chat: :class:`Chat`
    message: :class:`str`
    user: :class:`User`
    """

    chat = models.ForeignKey("chat.Chat", verbose_name=_("Chat"),
                             on_delete=models.CASCADE, related_name='messages')
    message = models.CharField(_("Message"), max_length=150)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"),
                             on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        verbose_name=_('Fecha creación'),
    )

    class Meta:
        verbose_name = _("chat Message")
        verbose_name_plural = _("chat Messages")
        models.UniqueConstraint(fields=['message', 'user', 'created_at'], name='unique_message_user_and_date')

    def __str__(self):
        return self.message

    def get_absolute_url(self):
        return reverse("chatmessage_detail", kwargs={"pk": self.pk})
