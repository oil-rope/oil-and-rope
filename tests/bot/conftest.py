import discord.ext.test as dpytest
import pytest

from bot.bot import OilAndRopeBot


@pytest.fixture(scope='function', autouse=False)
def bot(event_loop):
    bot = OilAndRopeBot(loop=event_loop)
    dpytest.configure(client=bot, num_guilds=1, num_channels=1, num_members=2)
    return bot
