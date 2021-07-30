import discord.ext.test as dpytest
import pytest
from django.conf import settings

from bot import bot as discord_bot


@pytest.fixture
def bot(event_loop):
    bot = discord_bot.OilAndRopeBot(loop=event_loop)
    dpytest.configure(client=bot, num_guilds=3, num_channels=3, num_members=3)
    return bot


@pytest.mark.asyncio
def test_bot_init_correctly_ok(bot):
    assert settings.BOT_COMMAND_PREFIX == bot.command_prefix
    assert settings.BOT_TOKEN == bot.token
    assert settings.BOT_DESCRIPTION == bot.description


@pytest.mark.asyncio
async def test_bot_on_ready(bot, mocker):
    spy = mocker.spy(bot, 'change_presence')
    await bot.on_ready()

    assert spy.call_count == 1
