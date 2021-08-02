import discord
import discord.ext.test as dpytest
import pytest
from discord.ext.commands.errors import CommandError, MissingRequiredArgument
from discord.ext.test.backend import make_message, make_user
from django.conf import settings

from bot.bot import OilAndRopeBot
from common.utils.faker import create_faker

fake = create_faker()


@pytest.fixture
def bot(event_loop):
    bot = OilAndRopeBot(loop=event_loop)
    dpytest.configure(client=bot, num_guilds=3, num_channels=3, num_members=3)
    return bot


@pytest.mark.asyncio
def test_bot_init_correctly_ok(bot):
    assert settings.BOT_COMMAND_PREFIX == bot.command_prefix
    assert settings.BOT_TOKEN == bot.token
    assert settings.BOT_DESCRIPTION == bot.description


@pytest.mark.asyncio
async def test_bot_on_ready_ok(bot, mocker):
    spy = mocker.spy(bot, 'change_presence')
    await bot.on_ready()

    assert spy.call_count == 1


@pytest.mark.asyncio
async def test_first_join_message_ok(bot, mocker):
    guild = bot.guilds[-1]
    user = make_user(fake.user_name(), fake.pyint(min_value=1, max_value=900))
    guild._add_member(user)
    guild._member_count += 1
    text_channel = guild.text_channels[0]

    mocker.patch('discord.channel.TextChannel.send')
    await bot.first_join_message(text_channel)

    discord.channel.TextChannel.send.assert_called_once_with(
        'Hello! You are about to experience a brand-new way to manage sessions and play!'
    )


@pytest.mark.asyncio
async def test_on_guild_join_ok(bot, mocker):
    guild = bot.guilds[-1]
    user = make_user(fake.user_name(), 123)
    guild._add_member(user)
    guild._member_count += 1

    mocker.patch('discord.channel.TextChannel.send')
    await bot.on_guild_join(guild)

    discord.channel.TextChannel.send.assert_called_once_with(
        'Hello! You are about to experience a brand-new way to manage sessions and play!'
    )


@pytest.mark.asyncio
async def test_on_message_ok(bot, mocker):
    msg_content = fake.word()
    msg_content = f'{bot.command_prefix}{msg_content}'
    user = make_user(fake.user_name(), 123)
    channel = bot.guilds[-1].channels[-1]
    message = make_message(msg_content, user, channel)
    mocker.patch('discord.ext.commands.Bot.on_message')
    await bot.on_message(message)

    discord.ext.commands.Bot.on_message.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_on_command_error_with_command_syntax_ok(bot, mocker):
    mocker.patch('discord.ext.commands.Context')
    context = mocker.AsyncMock()
    param = mocker.MagicMock()
    error = MissingRequiredArgument(param)
    await bot.on_command_error(context, error)

    context.send.assert_called_once_with('Incorrect format.')


@pytest.mark.asyncio
async def test_on_command_error_with_command_error_ok(bot, mocker):
    mocker.patch('discord.ext.commands.Context')
    context = mocker.AsyncMock()
    error_msg = fake.sentence()
    error = CommandError(error_msg)
    await bot.on_command_error(context, error)

    context.send.assert_called_once_with(error_msg)
