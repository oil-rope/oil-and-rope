import discord
import discord.ext.test as dpytest
import pytest
from discord.ext.commands import Bot
from django.conf import settings
from pytest_mock.plugin import MockerFixture

from common.utils.faker import create_faker

fake = create_faker()


def test_bot_init_correctly_ok(bot: Bot):
    assert settings.BOT_COMMAND_PREFIX == bot.command_prefix
    assert settings.BOT_TOKEN == bot.token
    assert settings.BOT_DESCRIPTION == bot.description


@pytest.mark.asyncio
async def test_bot_on_ready_ok(bot: Bot, mocker: MockerFixture):
    spy = mocker.spy(bot, 'change_presence')
    await bot.on_ready()

    assert spy.call_count == 1


@pytest.mark.asyncio
async def test_first_join_message_ok(bot: Bot, mocker: MockerFixture):
    guild = bot.guilds[-1]
    user = dpytest.backend.make_user(fake.user_name(), fake.pyint(min_value=1, max_value=900))
    guild._add_member(user)
    guild._member_count += 1
    text_channel = guild.text_channels[0]

    mocker.patch('discord.channel.TextChannel.send')
    await bot.first_join_message(text_channel)
    discord.channel.TextChannel.send.assert_called_once_with(
        'Hello! You are about to experience a brand-new way to manage sessions and play!'
    )


@pytest.mark.asyncio
async def test_on_guild_join_ok(bot: Bot, mocker: MockerFixture):
    guild = bot.guilds[-1]
    user = dpytest.backend.make_user(fake.user_name(), 123)
    guild._add_member(user)
    guild._member_count += 1

    mocker.patch('discord.channel.TextChannel.send')
    await bot.on_guild_join(guild)
    discord.channel.TextChannel.send.assert_called_once_with(
        'Hello! You are about to experience a brand-new way to manage sessions and play!'
    )
