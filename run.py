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

    owner = utils.get_or_create_discord_user(message.guild.owner)
    server = utils.get_or_create_discord_server(message.guild)
    if not server.discord_users.filter(id=owner.id).exists():
        server.discord_users.add(owner)

    user = utils.get_or_create_discord_user(message.author)
    if not server.discord_users.filter(id=user.id).exists():
        server.discord_users.add(user)

    breakpoint()
    await bot.logout()

bot.run(token)
