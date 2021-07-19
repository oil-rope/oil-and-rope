import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.apps import apps
from django.shortcuts import reverse
from model_bakery import baker
from rest_framework.authtoken.models import Token

from chat.consumers import ChatConsumer
from common.constants import models
from common.utils import create_faker

User = apps.get_model(models.USER_MODEL)

fake = create_faker()
url = reverse('chat:index')


@pytest.fixture(scope='function')
def user(db):
    return baker.make_recipe('registration.user')


@pytest.fixture(scope='function')
def token(user, db):
    return Token.objects.create(user=user)


@pytest.fixture(scope='function')
def chat(db):
    return baker.make_recipe('chat.chat')


@pytest.mark.asyncio
async def test_connect_ok():
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), url)
    connected, protocol = await communicator.connect()
    assert connected, 'WebSocket doesn\'t connect'

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_setup_channel_layer_ok(token, chat, async_client):
    await database_sync_to_async(async_client.force_login)(token.user)
    response = await async_client.get(url)
    request = response.asgi_request

    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), url)
    communicator.scope['session'] = request.session
    connected, protocol = await communicator.connect()
    assert connected, 'WebSocket doesn\'t connect'

    data = {
        'type': 'setup_channel_layer',
        'chat': chat.pk,
        'token': token.key,
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()
    await communicator.disconnect()

    assert 'info' == response['type']
    assert 'ok' == response['status']
    assert 'Chat connected!' == response['content']


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_send_message_ok(token, chat, async_client, settings):
    await database_sync_to_async(async_client.force_login)(token.user)
    response = await async_client.get(url)
    request = response.asgi_request

    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), url)
    communicator.scope['session'] = request.session
    connected, protocol = await communicator.connect()
    assert connected, 'WebSocket doesn\'t connect'

    data = {
        'type': 'setup_channel_layer',
        'chat': chat.pk,
        'token': token.key,
    }
    await communicator.send_json_to(data)
    await communicator.receive_json_from()

    data = {
        'type': 'send_message',
        'chat': chat.pk,
        'message': fake.word(),
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()
    communicator.disconnect()

    assert response['type'] == 'send_message'
    assert response['status'] == 'ok'
    assert response['content']['message'] == data['message']
    assert response['content']['author']['username'] == token.user.username
