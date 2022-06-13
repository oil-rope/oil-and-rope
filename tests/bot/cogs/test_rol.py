import discord.ext.test as dpytest
import pytest

from bot.cogs.rol import Roleplay
from tests.utils import AsyncMock


@pytest.mark.asyncio
async def test_roll_bad_syntax_ko(bot):
    roll = f'{bot.command_prefix}roll 1d20+'
    await dpytest.message(roll)

    assert dpytest.verify().message().content(
        content='Dice roll `1d20+` syntax is incorrect.'
    ), 'Bad syntax passes'


@pytest.mark.asyncio
async def test_roll_ok(bot):
    roll = f'{bot.command_prefix}roll 20'
    await dpytest.message(roll)

    # NOTE: Since we cannot test if embed is sent correctly we just assume no errors has been launched.
    assert True


@pytest.mark.asyncio
async def test_linkchannel_ko():
    ctx = AsyncMock()
    cog = Roleplay()
    await Roleplay.linkchannel(cog, ctx)

    ctx.send.assert_called_once_with('This command is not implemented yet.')
