from django.db import models
from django.utils.translation import gettext_lazy as _

from common.constants import models as constants
from core.models import TracingMixin


class DiscordUser(TracingMixin):
    """
    Model that manages Discord Users.

    Parameters
    ----------
    id: :class:`str`
        Identifier for the user (same as Discord).
    user: Optional[:class:`User`]
        User associated to this model if there's any.
    code: :class:`int`
        Code discriminator for the name.
    avatar_url: Optional[:class:`str`]
        URL to the Discord User's avatar.
    locale: Optional[:class:`str`]
        IETF language tag.
    premium: :class:`int`
        Declares if discord user is premium.
    created_at: :class:`datetime.datetime`
        Declares when user joined Discord.
    """

    id = models.CharField(verbose_name=_('identifier'), max_length=254, primary_key=True)
    user = models.OneToOneField(
        to=constants.USER_MODEL, verbose_name=_('user'), on_delete=models.CASCADE,
        related_name='discord_user', blank=True, null=True
    )
    nick = models.CharField(verbose_name=_('nick'), max_length=50)
    code = models.PositiveSmallIntegerField(verbose_name=_('code'))
    avatar_url = models.URLField(verbose_name=_('avatar'), max_length=254, null=True, blank=True)
    locale = models.CharField(verbose_name=_('locale'), max_length=10, null=True, blank=True)
    premium = models.BooleanField(verbose_name=_('premium'), default=False)
    created_at = models.DateTimeField(verbose_name=_('created at'))

    class Meta:
        verbose_name = _('discord user')
        verbose_name_plural = _('discord users')
        ordering = ['nick', '-created_at', '-entry_updated_at']

    def __str__(self):
        return '{}#{}'.format(self.nick, self.code)


class DiscordServer(TracingMixin):
    """
    Model that manages Discord Servers.

    Parameters
    ----------
    id: :class:`str`
        Identifier for the server.
    name: :class:`str`
        The name of the server.
    region: :class:`str`
        Declares region of the server.
    icon_url: Optional[:class:`str`]
        URL to the server's icon.
    owner: :class:`DiscordUser`
        Owner of the server.
    description: :class:`str`
        Description about the server.
    member_count: :class:`int`
        Quantity of members.
    created_at: :class:`datetime.datetime`
        Declares when the server was created.
    discord_users: List[:class:`DiscordUser`]
        List with all Discord Users in this server.
    """

    id = models.CharField(verbose_name=_('identifier'), max_length=254, primary_key=True)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    region = models.CharField(verbose_name=_('region'), max_length=20)
    icon_url = models.URLField(verbose_name=_('icon'), max_length=254, null=True, blank=True)
    owner = models.ForeignKey(
        to=constants.DISCORD_USER_MODEL, verbose_name=_('owner'), on_delete=models.CASCADE,
        related_name='owner_servers', db_index=True
    )
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    member_count = models.PositiveSmallIntegerField(verbose_name=_('member count'), default=0)
    created_at = models.DateTimeField(verbose_name=_('created at'))
    discord_users = models.ManyToManyField(
        to=constants.DISCORD_USER_MODEL, verbose_name=_('discord users'), related_name='discord_servers'
    )

    class Meta:
        verbose_name = _('discord server')
        verbose_name_plural = _('discord servers')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return 'Server {} ({})'.format(self.name, self.pk)


class DiscordChannelMixin(models.Model):
    """
    Base model for a Discord channel.

    Parameters
    ----------
    id: :class:`str`
        Identifier for the channel.
    name: :class:`str`
        The name of the channel.
    position: :class:`int`
        The position of the channel.
    created_at: :class:`datetime.datetime`
        Declares when the server was created.
    """

    id = models.CharField(verbose_name=_('identifier'), max_length=254, primary_key=True)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)
    created_at = models.DateTimeField(verbose_name=_('created at'))

    class Meta:
        abstract = True


class DiscordTextChannel(TracingMixin, DiscordChannelMixin):
    """
    Model that manages a Discord Text Channel.

    Parameters
    ----------
    id: :class:`str`
        Identifier for the channel.
    name: :class:`str`
        The name of the channel.
    position: :class:`int`
        The position of the channel.
    nsfw: :class:`bool`
        Declares if the channel is NSFW.
    topic: Optional[:class:`str`]
        Topic of the channel.
    news: :class:`bool`
        Declares is channel is New.
    created_at: :class:`datetime.datetime`
        Declares when the server was created.
    server: :class:`bot.DiscordServer`
        The serve where this text channel is hosted.
    discord_users: List[:class:`DiscordUser`]
        List with all Discord Users in this text channel.
    """

    nsfw = models.BooleanField(verbose_name=_('nsfw'), default=False, blank=True)
    topic = models.CharField(verbose_name=_('topic'), max_length=100, null=True, blank=True)
    news = models.BooleanField(verbose_name=_('news'), default=False, blank=True)
    server = models.ForeignKey(
        to=constants.DISCORD_SERVER_MODEL, verbose_name=_('discord server'), on_delete=models.CASCADE,
        related_name='discord_text_channels', db_index=True
    )
    discord_users = models.ManyToManyField(
        to=constants.DISCORD_USER_MODEL, verbose_name=_('discord users'), related_name='discord_text_channels'
    )

    class Meta:
        verbose_name = _('discord text channel')
        verbose_name_plural = _('discord text channels')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return 'Text Channel {} ({})'.format(self.name, self.pk)


class DiscordVoiceChannel(TracingMixin, DiscordChannelMixin):
    """
    Model that manages a Discord Voice Channel.

    Parameters
    ----------
    id: :class:`str`
        Identifier for the channel.
    name: :class:`str`
        The name of the channel.
    position: :class:`int`
        The position of the channel.
    bitrate: :class:`int`
        Declares the bitrate of the channel.
    created_at: :class:`datetime.datetime`
        Declares when the server was created.
    server: :class:`bot.DiscordServer`
        The serve where this voice channel is hosted.
    discord_users: List[:class:`DiscordUser`]
        List with all Discord Users in this voice channel.
    """

    bitrate = models.PositiveSmallIntegerField(verbose_name=_('bitrate'))
    server = models.ForeignKey(
        to=constants.DISCORD_SERVER_MODEL, verbose_name=_('discord server'), on_delete=models.CASCADE,
        related_name='discord_voice_channels', db_index=True
    )
    discord_users = models.ManyToManyField(
        to=constants.DISCORD_USER_MODEL, verbose_name=_('discord users'), related_name='discord_voice_channels',
        db_index=True
    )

    class Meta:
        verbose_name = _('discord voice channel')
        verbose_name_plural = _('discord voice channels')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return self.name
