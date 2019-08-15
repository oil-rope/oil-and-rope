import discord
import random
import os

from bot.bot import config

from discord.ext import commands

from bot.plugins import roll

#token = os.environ.get("DISCORD_BOT_SECRET")
#print(token)

configuration = config.Config()

client = commands.Bot(command_prefix=configuration.bot_prefix, self_bot=False)

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
async def on_message(message):
    await message.channel.send(roll.all(message))



client.run(configuration.token)