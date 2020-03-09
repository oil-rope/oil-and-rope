import os
import re

import discord
from discord.ext import commands

import django
from django.conf import settings
from django.utils import timezone

from bot.bot import config
from bot.plugins import roll

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')
django.setup()

configuration = config.Config()
prefix = configuration.configuration['Bot']['bot_prefix']
token = configuration.configuration['Credentials']['token']

bot = commands.Bot(command_prefix=prefix)
roll_pattern = r'^(?P<dice>\d*[Dd]\d+)(?P<modifier>[\+\-]((\d*[dD])?\d+))*'
roll_pattern = re.compile(roll_pattern)


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_member_join(member: discord.Member):
    print(f'{member} has joined the server.')


@bot.event
async def on_member_remove(member: discord.Member):
    print(f'{member} has left the server.')


@bot.event
async def on_guild_join(self, ctx, *, guild_id):
    from bot import models
    guild = discord.utils.get(self.bot.guilds, id=guild_id)
    try:
        actual_guild = models.DiscordServer.objects.get(pk=guild.id)
    except models.DiscordServer.DoesNotExist:
        actual_guild = models.DiscordServer(
            id=guild.id
        )
    print("Hi! I'm a lorem ipsum")


@bot.event
async def on_message(message: discord.Message):
    # Separating variables
    author = message.author
    channel = message.channel
    content = message.content
    guild = message.guild

    if content.startswith(prefix):
        if not author.bot:
            from bot import models

            # First of all we get commands
            await bot.process_commands(message)

            # A log
            print(f'{author}: {content}')

            # Getting or creating user object
            user = models.DiscordUser.objects.get_or_create(
                id=author.id,
                defaults={
                    'nick': author.nick or author.name,
                    'code': author.discriminator,
                    'avatar_url': author.avatar_url or None,
                    'locale': settings.LANGUAGE_CODE,
                    'created_at': timezone.make_aware(author.created_at)
                },
            )[0]

            # Getting server owner
            owner = models.DiscordUser.objects.get_or_create(
                id=guild.owner.id,
                defaults={
                    'nick': guild.owner.nick or guild.owner.name,
                    'code': guild.owner.discriminator,
                    'avatar_url': guild.owner.avatar_url or None,
                    'locale': settings.LANGUAGE_CODE,
                    'created_at': timezone.make_aware(guild.owner.created_at)
                },
            )[0]

            # Getting or creating server object
            server = models.DiscordServer.objects.get_or_create(
                id=guild.id,
                defaults={
                    'name': guild.name,
                    'region': guild.region,
                    'icon_url': guild.icon_url,
                    'owner': owner,
                    'description': guild.description,
                    'member_count': guild.member_count,
                    'created_at': timezone.make_aware(guild.created_at),
                },
            )[0]

            # Checking if user is in Server at Database-level
            if user not in server.discord_users.all():
                server.discord_users.add(user)
            # Checking if owner is in Server at Database-level
            if owner not in server.discord_users.all():
                server.discord_users.add(owner)

            # Getting or creating text_channel
            text_channel = models.DiscordTextChannel.objects.get_or_create(
                id=channel.id,
                defaults={
                    'name': channel.name,
                    'position': channel.position,
                    'server': server,
                    'nsfw': channel.nsfw,
                    'topic': channel.topic,
                    'news': channel.is_news(),
                    'created_at': timezone.make_aware(channel.created_at),
                },
            )[0]

            # Checking if user is in text channel at Database-level
            if user not in text_channel.discord_users.all():
                text_channel.discord_users.add(user)

            # Removing whitespaces
            roll_message = content.replace(' ', '')
            roll_message = roll_message.replace(prefix, '', 1)

            # Shortcut for roll function
            if roll_pattern.match(roll_message):
                await channel.send(roll.all(message))


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    from bot import models

    author = member
    channel = member.voice.channel
    guild = channel.guild

    # Getting or creating user object
    user = models.DiscordUser.objects.get_or_create(
        id=author.id,
        defaults={
            'nick': author.nick or author.name,
            'code': author.discriminator,
            'avatar_url': author.avatar_url or None,
            'locale': settings.LANGUAGE_CODE,
            'created_at': timezone.make_aware(author.created_at)
        },
    )[0]

    # Getting server owner
    owner = models.DiscordUser.objects.get_or_create(
        id=guild.owner.id,
        defaults={
            'nick': guild.owner.nick or guild.owner.name,
            'code': guild.owner.discriminator,
            'avatar_url': guild.owner.avatar_url or None,
            'locale': settings.LANGUAGE_CODE,
            'created_at': timezone.make_aware(guild.owner.created_at)
        },
    )[0]

    # Getting or creating server object
    server = models.DiscordServer.objects.get_or_create(
        id=guild.id,
        defaults={
            'name': guild.name,
            'region': guild.region,
            'icon_url': guild.icon_url,
            'owner': owner,
            'description': guild.description,
            'member_count': guild.member_count,
            'created_at': timezone.make_aware(guild.created_at),
        },
    )[0]

    # Checking if user is in Server at Database-level
    if user not in server.discord_users.all():
        server.discord_users.add(user)

    # Getting or creating Voice Channel
    voice_channel = models.DiscordVoiceChannel.objects.get_or_create(
        id=channel.id,
        defaults={
            'name': channel.name,
            'position': channel.position,
            'bitrate': channel.bitrate,
            'created_at': timezone.make_aware(channel.created_at),
        },
    )[0]
    if user not in voice_channel.discord_users.all():
        voice_channel.discord_users.add(user)

bot.run(token)
