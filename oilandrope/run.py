import os
import random
import re

import discord
import django
from discord.ext import commands
from django.conf import settings
from django.utils import timezone

from bot.bot import config
from bot.plugins import roll

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oilandrope.settings')
django.setup()

configuration = config.Config()
prefix = configuration.configuration['Bot']['bot_prefix']
token = configuration.configuration['Credentials']['token']

client = commands.Bot(command_prefix=prefix)
roll_pattern = r'^(?P<dice>\d*[Dd]\d+)(?P<modifier>[\+\-]((\d*[dD])?\d+))*'
roll_pattern = re.compile(roll_pattern)


@client.event
async def on_ready():
    print('Bot is ready.')


@client.event
async def on_member_join(member):
    print('{member} has joined the server.'.format(member=member))


@client.event
async def on_member_remove(member):
    print('{member} has left the server.'.format(member=member))


@client.event
async def on_guild_join(self, ctx, *, guild_id):
    from bot import models
    guild = discord.utils.get(self.bot.guilds, id=guild_id)
    try:
        actual_guild = models.DiscordServer.objects.get(pk=guild.id)
    except models.DiscordServer.DoesNotExist:
        actual_guild = models.DiscordServer(
            id = guild.id
        )
    print("Hi! I'm a lorem ipsum")


@client.event
async def on_message(message: discord.Message):

    from bot import models
    author = message.author
    channel = message.channel
    content = message.content
    guild = message.guild


    if not author.bot:
        if message.content.startswith(prefix):

            user = models.DiscordUser.objects.get_or_create(
                id = author.id,
                defaults = {
                    'nick': author.nick or author.name,
                    'code': author.discriminator,
                    'avatar_url': author.avatar_url or None,
                    'locale': settings.LANGUAGE_CODE,
                    'created_at': timezone.make_aware(author.created_at)
                },
            )[0]

            owner = models.DiscordUser.objects.get_or_create(
                id = guild.owner.id,
                defaults = {
                    'nick': guild.owner.nick or guild.owner.name,
                    'code': guild.owner.discriminator,
                    'avatar_url': guild.owner.avatar_url or None,
                    'locale': settings.LANGUAGE_CODE,
                    'created_at': timezone.make_aware(guild.owner.created_at)

                },
            )[0]


            server = models.DiscordServer.objects.get_or_create(
                id = guild.id,
                defaults = {
                    'name': guild.name,
                    'region': guild.region,
                    'icon_url': guild.icon_url,
                    'owner': models.DiscordUser.objects.get(pk=guild.owner.id),
                    'description': guild.description,
                    'member_count': guild.member_count,
                    'created_at': guild.created_at,
                },
            )[0]
            server.discord_users.add(user)

            text_channel = models.DiscordTextChannel.objects.get_or_create(
                id = channel.id,
                defaults = {
                    'name': channel.name,
                    'position': channel.position,
                    'created_at': channel.created_at,

                    'nsfw': channel.nsfw,
                    'topic': channel.topic,
                    'news': channel.is_news()
                },
            )[0]
            text_channel.discord_users.add(user)

            roll_message = message.content.replace(" ", "").replace(prefix, '', 1)
            if roll_pattern.match(roll_message):
                await channel.send(roll.all(message))


@client.event
async def on_voice_state_update(member, before, after):
    from bot import models

    channel = member.voice.channel
    user = models.DiscordUser.objects.get(pk=member.id)

    voice_channel = models.DiscordVoiceChannel.objects.get_or_create(
        id = channel.id,
        defaults = {
            'name': channel.name,
            'position': channel.position,
            'created_at': channel.created_at,

            'bitrate': channel.bitrate
        },
    )[0]
    voice_channel.discord_users.add(user)

    #import pdb; pdb.set_trace()


client.run(token)
