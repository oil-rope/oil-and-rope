import discord
import django
from discord.ext import commands

from bot import config, utils

django.setup()

configuration = config.Config()
prefix = configuration.configuration['Bot']['bot_prefix']
token = configuration.configuration['Credentials']['token']

bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print('{bot} is ready!'.format(
        bot=bot.user.name
    ))


@bot.event
async def on_message(message: discord.Message):
    # Avoid everything out scope of our prefix
    if not message.content.startswith(prefix):
        return

    # Getting and registering owner
    owner = utils.get_or_create_discord_user(message.guild.owner)

    # Getting and registering channel
    channel = utils.get_or_create_discord_text_channel(message.channel, message.guild)
    if not channel.discord_users.filter(id=owner.id).exists():
        channel.discord_users.add(owner)

    # Getting and registering server
    server = utils.get_or_create_discord_server(message.guild)
    if not server.discord_users.filter(id=owner.id).exists():
        server.discord_users.add(owner)

    user = utils.get_or_create_discord_user(message.author)
    if user.id != owner.id:
        if not channel.discord_users.filter(id=owner.id).exists():
            channel.discord_users.add(owner)
        if not server.discord_users.filter(id=user.id).exists():
            server.discord_users.add(user)

    await bot.logout()

bot.run(token)
