import logging

from django.apps import apps
from django.conf import settings
from django.shortcuts import reverse
from django.utils.timezone import is_naive, make_aware

from common.tools.sync import async_get, async_get_or_create

LOGGER = logging.getLogger(__name__)


async def get_or_create_discord_user(member):
    """
    Searches in database for the given user or creates one if not found.

    Parameters
    ----------
    member: :class:`abc.User`
        Discord API abstract user.

    Returns
    -------
    user: :class:`models.DiscordUser`
        The user fetched.
    """

    if not hasattr(member, 'premium_since'):  # pragma: no cover
        premium_since = None
    else:
        premium_since = member.premium_since

    created_at = member.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    # Importing DiscordUser inside a function to avoid 'Apps not ready'
    DiscordUser = apps.get_model('bot.DiscordUser')

    defaults = {
        'nick': member.display_name,
        'code': member.discriminator,
        'avatar_url': member.avatar_url or None,
        'locale': settings.LANGUAGE_CODE or None,
        'premium': True if premium_since else False,
        'created_at': created_at
    }
    user, created = await async_get_or_create(DiscordUser, id=member.id, defaults=defaults)

    if created:
        logging.info('User %s created', user)

    return user


async def get_or_create_discord_server(guild):
    """
    Searches in database for the given server or creates one if not found.

    Parameters
    ----------
    guild: :class:`discord.Guild`
        Discord API Guild.

    Returns
    -------
    server: :class:`models.DiscordServer`
        The server fetched.
    """

    created_at = guild.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    # Importing DiscordServer inside a function to avoid 'Apps not ready'
    DiscordServer = apps.get_model('bot.DiscordServer')

    defaults = {
        'name': guild.name,
        'region': guild.region.value,
        'icon_url': guild.icon_url or None,
        'owner_id': guild.owner_id,
        'description': guild.description or None,
        'member_count': guild.member_count,
        'created_at': created_at
    }
    server, created = await async_get_or_create(DiscordServer, id=guild.id, defaults=defaults)

    if created:
        logging.info('Server %s created', server)

    return server


async def get_or_create_discord_text_channel(channel, guild):
    """
    Searches in database for the given text channel or creates one if not found.

    Parameters
    ----------
    channel: :class:`discord.channel.TextChannel`
        Discord API TextChannel.
    guild: :class:`discord.Guild`
        Discord API Guild.

    Returns
    -------
    text_channel: :class:`models.DiscordTextChannel`
        The text channel fetched.
    """

    created_at = channel.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    # Importing DiscordTextChannel inside a function to avoid 'Apps not ready'
    DiscordTextChannel = apps.get_model('bot.DiscordTextChannel')

    defaults = {
        'name': channel.name,
        'position': channel.position,
        'nsfw': channel.is_nsfw(),
        'topic': channel.topic or None,
        'news': channel.is_news(),
        'created_at': created_at,
        'server_id': guild.id
    }
    text_channel, created = await async_get_or_create(DiscordTextChannel, id=channel.id, defaults=defaults)

    if created:
        logging.info('Text Channel %s created', text_channel)

    return text_channel


async def get_url_from(resolver, site_id=settings.SITE_ID, secure=settings.DEBUG, kwargs=None):
    """
    Constructs absolute URL from given params.
    """

    Site = apps.get_model('sites.Site')
    site = await async_get(Site, pk=site_id)
    http_protocol = 'http://' if secure else 'http://'
    if kwargs:
        reverse_url = reverse(resolver, kwargs=kwargs)
    else:
        reverse_url = reverse(resolver)
    url = f'{http_protocol}{site.domain}{reverse_url}'

    return url
