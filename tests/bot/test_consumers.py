"""
:class:`unittest.TestCase` are not compatible with WebSockets Consumers (DjangoChannels) so tests must
written as top-level functions.
"""

import faker
import pytest
from channels.testing import WebsocketCommunicator
from django.shortcuts import reverse

from bot.consumers import BotConsumer

fake = faker.Faker()


@pytest.fixture(scope='function', autouse=False)
def url():
    return reverse('registration:register')


@pytest.mark.asyncio
async def test_websocket_connect(url):
    communicator = WebsocketCommunicator(BotConsumer, url)
    connected, subprotocol = await communicator.connect()
    assert connected, 'WebSocket is not connected.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_discord_user_does_not_exist(url):
    communicator = WebsocketCommunicator(BotConsumer, url)
    data = {
        'type': 'check_user',
        'discord_id': fake.random_int()
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()
    assert 'exists' in response, 'Key \'exists\' does not exist.'
    assert not response['exists'], 'Discord ID check as existent.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_discord_user_exists(url, discord_user):
    communicator = WebsocketCommunicator(BotConsumer, url)
    data = {
        'type': 'check_user',
        'discord_id': discord_user.id
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()
    assert 'exists' in response, 'Key \'exists\' does not exist.'
    assert response['exists'], 'Discord ID check as non existent.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()
