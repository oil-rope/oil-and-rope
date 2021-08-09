import discord.ext.test as dpytest
import pytest


@pytest.mark.asyncio
async def test_shutdown_not_owner_ko(bot):
    await dpytest.message(f'{bot.command_prefix}shutdown')
    assert dpytest.verify().message().content('You don\'t have permission to perform this command.')


@pytest.mark.asyncio
async def test_shutdown_owner_ok(bot, mocker):
    mocker.patch('discord.ext.commands.Bot.is_owner', mocker.AsyncMock(return_value=True))
    mocker.patch('discord.ext.commands.Bot.close', mocker.AsyncMock())
    await dpytest.message(content=f'{bot.command_prefix}shutdown')
    assert dpytest.verify().message().content('Shutting down...')
