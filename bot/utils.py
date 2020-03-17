import logging

import discord
from discord import abc
from django.conf import settings
from django.utils.timezone import make_aware

LOGGER = logging.getLogger(__name__)


def validate(*validations):
    """
    Checks if all `validations` are correct before executing.
    """

    def message_validation(func):
        def func_wrapper(*args, **kwargs):
            if all(validations):
                func(*args, **kwargs)
        return func_wrapper
    return message_validation


def get_or_create_discord_user(member: abc.User):
    """
    Searches in database for the given user or creates one if not found.

    member: :class:`abc.User`
        Discord API abstract user.
    """

    # Importing DiscordUser inside a function to avoid 'Apps not ready'
    from .models import DiscordUser

    user, created = DiscordUser.objects.get_or_create(
        id=member.id,
        defaults={
            'nick': member.display_name,
            'code': member.discriminator,
            'avatar_url': member.avatar_url or None,
            'locale': settings.LANGUAGE_CODE or None,
            'premium': True if member.premium_since else False,
            'created_at': make_aware(member.created_at)
        }
    )

    if created:
        logging.info('User %s created', user)

    return user


def get_or_create_discord_server(guild: discord.Guild):
    """
    Searches in database for the given server or creates one if not found.

    guild: :class:`discord.Guildl`
        Discord API Guild.
    """

    # Importing DiscordServer inside a function to avoid 'Apps not ready'
    from .models import DiscordServer

    server, created = DiscordServer.objects.get_or_create(
        id=guild.id,
        defaults={
            'name': guild.name,
            'region': guild.region.value,
            'icon_url': guild.icon_url or None,
            'owner_id': guild.owner_id,
            'description': guild.description or None,
            'member_count': guild.member_count,
            'created_at': make_aware(guild.created_at)
        }
    )

    if created:
        logging.info('Server %s created', server)

    return server
