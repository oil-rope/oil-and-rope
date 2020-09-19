import faker
import pytest
from channels.testing import WebsocketCommunicator
from django.shortcuts import reverse
from model_bakery import baker

from chat.consumers import ChatConsumer
from common.constants import models
from chat.models import ChatMessage

fake = faker.Faker()


@pytest.fixture(scope='function', autouse=False)
def url():
    return reverse('chat:index')


@pytest.mark.asyncio
async def test_websocket_connect(url):
    communicator = WebsocketCommunicator(ChatConsumer, url)
    connected, subprotocol = await communicator.connect()
    assert connected, 'WebSocket is not connected.'

    # Disconnect WebSocket to avoid pending tasks
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_setup_channel_layer(url):
    communicator = WebsocketCommunicator(ChatConsumer, url)

    chat = baker.make(models.CHAT_MODEL)
    data = {
        'type': 'setup_channel_layer',
        'chat': chat.pk,
    }
    await communicator.send_json_to(data)

    # Disconnect communicator
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_send_message_without_setup(url):
    user = baker.make(models.USER_MODEL)
    communicator = WebsocketCommunicator(ChatConsumer, url)
    communicator.scope['user'] = user

    chat = baker.make(models.CHAT_MODEL)
    data = {
        'type': 'send_message',
        'chat': chat.pk,
        'message': fake.word(),
    }
    await communicator.send_json_to(data)

    with pytest.raises(TypeError):
        await communicator.receive_json_from()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_send_message(url):
    user = baker.make(models.USER_MODEL)
    communicator = WebsocketCommunicator(ChatConsumer, url)
    communicator.scope['user'] = user

    chat = baker.make(models.CHAT_MODEL)
    # Setup
    data = {
        'type': 'setup_channel_layer',
        'chat': chat.pk,
    }
    await communicator.send_json_to(data)

    word = fake.word()
    data = {
        'type': 'send_message',
        'chat': chat.pk,
        'message': word,
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()

    assert word == response['message']
    assert chat.pk == response['chat']

    assert ChatMessage.objects.get(pk=response['id'])

    # Disconnect
    await communicator.disconnect()
