"""
Oil & Rope
~~~~~~~~~~

A bot connected to Oil & Rope web to make Roleplay Games more interactive.
"""

import logging
from datetime import datetime

import discord
from discord.ext import commands

LOGGER = logging.getLogger(__name__)


class OilAndRopeBot(commands.Bot):
    """
    """

    def __init__(self, *args, **kwargs):
        super(OilAndRopeBot, self).__init__(*args, **kwargs)

    async def on_ready(self):
        init_message = '{bot} is ready!\nID: {id}\nAt {time}'.format(
            bot=self.user.name,
            id=self.user.id,
            time=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        print(init_message)

    async def on_message(self, message: discord.Message):
        log_message = '{author} ({id}): {message}'.format(
            author=message.author.name,
            id=message.author.id,
            message=message.content
        )
        print(log_message)
        await super(OilAndRopeBot, self).on_message(message)
