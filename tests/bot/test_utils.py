
import pytest
from django.contrib.sites.models import Site
from django.shortcuts import reverse

from bot.models import DiscordServer, DiscordTextChannel, DiscordUser
from bot.utils import (get_or_create_discord_server, get_or_create_discord_text_channel, get_or_create_discord_user,
                       get_url_from)
from common.tools.sync import async_get

from .helpers import mocks
from model_bakery import baker


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_or_create_discord_user_ok():
    member = mocks.MemberMock()

    discord_user = await get_or_create_discord_user(member)
    await async_get(DiscordUser, pk=discord_user.pk)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_or_create_discord_server_ok():
    guild = mocks.GuildMock()
    member = guild.owner
    await get_or_create_discord_user(member)

    discord_server = await get_or_create_discord_server(guild)
    await async_get(DiscordServer, pk=discord_server.pk)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_or_create_discord_text_channel_ok():
    channel = mocks.TextChannelMock()
    guild = channel.guild
    member = guild.owner
    await get_or_create_discord_user(member)
    await get_or_create_discord_server(guild)

    discord_text_channel = await get_or_create_discord_text_channel(channel, guild)
    await async_get(DiscordTextChannel, pk=discord_text_channel.pk)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_url_from_without_kwargs_ok():
    site = Site.objects.first()
    url = reverse('core:home')
    expected = f'http://{site.domain}{url}'
    result = await get_url_from('core:home')

    assert expected == result


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_url_from_with_kwargs_ok():
    # We setup a world for testing
    world = baker.make('roleplay.Place')
    url = reverse('roleplay:world_detail', kwargs={'pk': world.pk})

    site = Site.objects.first()
    expected = f'http://{site.domain}{url}'
    result = await get_url_from('roleplay:world_detail', kwargs={'pk': world.pk})

    assert expected == result
