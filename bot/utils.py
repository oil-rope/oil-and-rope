import logging

import discord
from discord import abc
from django.conf import settings
from django.utils.timezone import is_naive, make_aware

from . import exceptions

LOGGER = logging.getLogger(__name__)


def get_or_create_discord_user(member: abc.User):
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

    if not member:
        raise exceptions.OilAndRopeException('Discord User cannot be None.')

    if not hasattr(member, 'premium_since'):  # pragma: no cover
        premium_since = None
    else:
        premium_since = member.premium_since

    created_at = member.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    # Importing DiscordUser inside a function to avoid 'Apps not ready'
    from .models import DiscordUser

    user, created = DiscordUser.objects.get_or_create(
        id=member.id,
        defaults={
            'nick': member.display_name,
            'code': member.discriminator,
            'avatar_url': member.avatar_url or None,
            'locale': settings.LANGUAGE_CODE or None,
            'premium': True if premium_since else False,
            'created_at': created_at
        }
    )

    if created:
        logging.info('User %s created', user)

    return user


def get_or_create_discord_server(guild: discord.Guild):
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

    # Importing DiscordServer inside a function to avoid 'Apps not ready'
    from .models import DiscordServer

    created_at = guild.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    server, created = DiscordServer.objects.get_or_create(
        id=guild.id,
        defaults={
            'name': guild.name,
            'region': guild.region.value,
            'icon_url': guild.icon_url or None,
            'owner_id': guild.owner_id,
            'description': guild.description or None,
            'member_count': guild.member_count,
            'created_at': created_at
        }
    )

    if created:
        logging.info('Server %s created', server)

    return server


def get_or_create_discord_text_channel(channel: discord.channel.TextChannel, guild: discord.Guild):
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

    # Importing DiscordTextChannel inside a function to avoid 'Apps not ready'
    from .models import DiscordTextChannel

    created_at = channel.created_at
    if is_naive(created_at):
        created_at = make_aware(created_at)

    text_channel, created = DiscordTextChannel.objects.get_or_create(
        id=channel.id,
        defaults={
            'name': channel.name,
            'position': channel.position,
            'nsfw': channel.is_nsfw(),
            'topic': channel.topic or None,
            'news': channel.is_news(),
            'created_at': created_at,
            'server_id': guild.id
        }
    )

    if created:
        logging.info('Text Channel %s created', text_channel)

    return text_channel
