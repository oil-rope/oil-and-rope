from unittest import mock

import pytest
from django.apps import apps
from django.conf import settings
from model_bakery import baker

from bot.commands.roleplay import world_list
from bot.models import DiscordUser
from common.tools.sync import async_manager_func
from common.tools.sync.models import async_get
from tests.bot.helpers import mocks

Place = apps.get_model('roleplay.Place')
User = apps.get_model(settings.AUTH_USER_MODEL)


@pytest.fixture(scope='function')
def registered_author():
    author = mocks.MemberMock()
    user = baker.make(User)
    discord_user = baker.make(DiscordUser, id=author.id)
    discord_user.user = user
    discord_user.save()
    return author


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@mock.patch('tests.bot.helpers.mocks.MemberMock.send')
async def test_world_list_private_ok(mock_call, registered_author):
    # Setup the user
    author = registered_author
    user = await async_get(User, discord_user__id=author.id)

    # Setup actual call
    baker.make(Place, 2, user=user, owner=user)
    worlds = await async_manager_func(Place, 'user_places', user=user)
    worlds = ', '.join(f'*{world.name}*' for world in worlds)
    worlds_expected = f'Here\'s a list of your worlds: {worlds}.'
    info_msg_expected = 'Remember you can get a better display at the web: http://example.com/en/roleplay/place/'

    await world_list(author)
    mock_call.assert_has_calls([
        mock.call(worlds_expected),
        mock.call(info_msg_expected),
    ])


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@mock.patch('tests.bot.helpers.mocks.MemberMock.send')
async def test_world_list_empty_ok(mock_call):
    author = mocks.MemberMock()
    worlds_expected = 'Seems like there isn\'t any world yet.'
    info_msg_expected = 'Remember you can get a better display at the web: http://example.com/en/roleplay/place/'

    await world_list(author)
    mock_call.assert_has_calls([
        mock.call(worlds_expected),
        mock.call(info_msg_expected),
    ])


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@mock.patch('tests.bot.helpers.mocks.MemberMock.send')
async def test_world_list_public_ok(mock_call, registered_author):
    author = registered_author
    user = await async_get(User, discord_user__id=author.id)
    baker.make(Place, 2, user=None, owner=None)
    baker.make(Place, 2, user=user, owner=user)
    worlds = await async_manager_func(Place, 'community_places')
    worlds = ', '.join(f'*{world.name}*' for world in worlds)
    worlds_expected = f'Here\'s a list of your worlds: {worlds}.'
    info_msg_expected = 'Remember you can get a better display at the web: http://example.com/en/roleplay/place/'

    await world_list(author, public=True)
    mock_call.assert_has_calls([
        mock.call(worlds_expected),
        mock.call(info_msg_expected),
    ])
