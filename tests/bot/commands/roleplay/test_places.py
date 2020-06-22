from unittest import mock

import pytest
from django.apps import apps
from model_bakery import baker

from bot.commands.roleplay import world_list
from bot.commands.roleplay.places import world_delete
from bot.models import DiscordUser
from bot.utils import get_url_from
from common.constants.models import PLACE_MODEL, USER_MODEL
from common.tools.sync import async_manager_func
from common.tools.sync.models import async_get
from tests.bot.helpers import mocks

Place = apps.get_model(PLACE_MODEL)
User = apps.get_model(USER_MODEL)


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


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@mock.patch('tests.bot.helpers.mocks.MemberMock.send')
async def test_world_delete_ok(mock_call, registered_author):
    author = registered_author
    # We use 1 for convention (to make check == 1 -> True), is indeed NOT RECOMMENDED
    deleted_world = 1
    bot = mocks.ClientMock(ignore_check_wait_for=True, wait_for_default=str(deleted_world))
    user = await async_get(User, discord_user__id=author.id)
    baker.make(Place, 2, user=user, owner=user)
    worlds = await async_manager_func(Place, 'own_places', user=user)
    deleted_world = worlds[1]

    await world_delete(author, bot)
    with pytest.raises(Place.DoesNotExist):
        await async_get(Place, pk=deleted_world.pk)

    all_calls = mock_call.mock_calls
    expected_delete_msg = f'Are you sure you want to delete {deleted_world}? [yes/no]'
    assert mock.call(expected_delete_msg) in all_calls
    del_url = await get_url_from('roleplay:world_delete', kwargs={'pk': deleted_world.pk})
    info_msg = f'You can perform this action via web: {del_url}'
    assert mock.call(info_msg) in all_calls
    del_msg = f'{deleted_world} deleted.'
    assert mock.call(del_msg) in all_calls


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
@mock.patch('tests.bot.helpers.mocks.MemberMock.send')
async def test_world_delete_empty(mock_call, registered_author):
    author = registered_author
    bot = mocks.ClientMock()
    await world_delete(author, bot)

    all_calls = mock_call.mock_calls
    empty_msg = 'Seems like you don\'t have any world yet.'
    assert mock.call(empty_msg) in all_calls
