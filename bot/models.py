from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

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

    id = models.CharField(_('Identifier'), max_length=254, primary_key=True)
    user = models.OneToOneField("auth.User", verbose_name=_('User'), on_delete=models.CASCADE,
                                related_name='discord_user', blank=True, null=True)
    nick = models.CharField(_('Nick'), max_length=50)
    code = models.PositiveSmallIntegerField(_('Code'))
    avatar_url = models.URLField(_('Avatar URL'), max_length=254, null=True, blank=True)
    locale = models.CharField(_('Locale'), max_length=10, null=True, blank=True)
    premium = models.BooleanField(_('Premium'), default=False)
    created_at = models.DateTimeField(_('Created at'))

    class Meta:
        verbose_name = _('Discord User')
        verbose_name_plural = _('Discord Users')
        ordering = ['nick', '-created_at', '-entry_updated_at']

    def __str__(self):
        return '{}#{}'.format(self.nick, self.code)

    def get_absolute_url(self):
        return reverse('bot:discorduser_detail', kwargs={'pk': self.pk})


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

    id = models.CharField(_('Identifier'), max_length=254, primary_key=True)
    name = models.CharField(_('Name'), max_length=50)
    region = models.CharField(_('Region'), max_length=20)
    icon_url = models.URLField(_('Icon URL'), max_length=254, null=True, blank=True)
    owner = models.ForeignKey('bot.DiscordUser', verbose_name=_('Owner'), on_delete=models.CASCADE,
                              related_name='owner_servers', db_index=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    member_count = models.PositiveSmallIntegerField(_('Member count'), default=0)
    created_at = models.DateTimeField(_('Created at'))
    discord_users = models.ManyToManyField('bot.DiscordUser', verbose_name=_('Discord Users'),
                                           related_name='discord_servers')

    class Meta:
        verbose_name = _('Discord Server')
        verbose_name_plural = _('Discord Servers')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return 'Server {} ({})'.format(self.name, self.pk)

    def get_absolute_url(self):
        return reverse('bot:discordserver_detail', kwargs={'pk': self.pk})


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

    id = models.CharField(_('Identifier'), max_length=254, primary_key=True)
    name = models.CharField(_('Name'), max_length=50)
    position = models.PositiveSmallIntegerField(_('Position'), default=0)
    created_at = models.DateTimeField(_('Created at'))

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

    nsfw = models.BooleanField(_('NSFW'), default=False, blank=True)
    topic = models.CharField(_('Topic'), max_length=100, null=True, blank=True)
    news = models.BooleanField(_('News'), default=False, blank=True)
    server = models.ForeignKey("bot.DiscordServer", verbose_name=_("Discord Server"),
                               on_delete=models.CASCADE, related_name='discord_text_channels')
    discord_users = models.ManyToManyField('bot.DiscordUser', verbose_name=_('Discord Users'),
                                           related_name='discord_text_channels')

    class Meta:
        verbose_name = _('Discord Text Channel')
        verbose_name_plural = _('Discord Text Channels')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return 'Text Channel {} ({})'.format(self.name, self.pk)

    def get_absolute_url(self):
        return reverse('bot:discordchanneltext_detail', kwargs={'pk': self.pk})


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

    bitrate = models.PositiveSmallIntegerField(_('Bitrate'))
    server = models.ForeignKey("bot.DiscordServer", verbose_name=_("Discord Server"),
                               on_delete=models.CASCADE, related_name='discord_voice_channels')
    discord_users = models.ManyToManyField('bot.DiscordUser', verbose_name=_('Discord Users'),
                                           related_name='discord_voice_channels')

    class Meta:
        verbose_name = _('Discord Voice Channel')
        verbose_name_plural = _('Discord Voice Channels')
        ordering = ['name', '-created_at', '-entry_updated_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bot:discordvoicechannel_detail', kwargs={'pk': self.pk})
