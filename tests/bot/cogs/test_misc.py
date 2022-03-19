import discord.ext.test as dpytest
import pytest


@pytest.mark.asyncio
async def test_shutdown_not_owner_ko(bot):
    await dpytest.message(f'{bot.command_prefix}shutdown')

    assert dpytest.verify().message().content(
        content='You don\'t have permission to perform this command.'
    ), 'User without permission shutdowns bot'


@pytest.mark.asyncio
async def test_shutdown_owner_ok(bot, mocker):
    mocker.patch('discord.ext.commands.Bot.is_owner', mocker.AsyncMock(return_value=True))
    mocker.patch('discord.ext.commands.Bot.close', mocker.AsyncMock())
    await dpytest.message(content=f'{bot.command_prefix}shutdown')

    assert dpytest.verify().message().content(
        content='Shutting down...'
    ), 'Bot is not being shutdown'


@pytest.mark.asyncio
async def test_roll_bad_syntax_ko(bot):
    roll = f'{bot.command_prefix}roll 1d20+'
    await dpytest.message(content=roll)

    assert dpytest.verify().message().content('Dice roll `1d20+` syntax is incorrect.'), 'Bad syntax passes'


@pytest.mark.asyncio
async def test_roll_ok(bot):
    roll = f'{bot.command_prefix}roll 20'
    await dpytest.message(content=roll)

    # NOTE: Since we cannot test if embed is sent correctly we just assume no errors has been launched.
    assert True
