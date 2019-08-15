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

#token = os.environ.get("DISCORD_BOT_SECRET")
# print(token)

configuration = config.Config()

client = commands.Bot(command_prefix=configuration.bot_prefix, self_bot=False)
roll_pattern = re.compile(
    '^(?P<dice>\d*[Dd]\d+)(?P<modifier>[\+\-]((\d*[dD])?\d+))*')


@client.event
async def on_ready():
    print('Bot is ready.')


@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')


@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')


@client.event
async def on_message(message: discord.Message):
    from bot import models
    author = message.author
    channel = message.channel
    content = message.content

    if not author.bot:
        try:
            user = models.DiscordUser.objects.get(pk=author.id)
        except models.DiscordUser.DoesNotExist:
            user = models.DiscordUser(
                id=author.id,
                nick=author.nick or author.name,
                code=author.discriminator,
                avatar_url=author.avatar_url or None,
                locale=settings.LANGUAGE_CODE,
                created_at=timezone.make_aware(author.created_at)
            )
            user.save()
        if user.user:
            print(user.user)
            import pdb; pdb.set_trace()

        roll_mesage = content.strip().replace(configuration.bot_prefix, '', 1)
        if roll_pattern.match(roll_mesage):
            await channel.send(roll.all(message))


client.run(configuration.token)
