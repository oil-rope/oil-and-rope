import faker
import pytest
from channels.testing import WebsocketCommunicator
from django.shortcuts import reverse
from model_bakery import baker

from chat.consumers import ChatConsumer
from chat.models import ChatMessage
from common.constants import models

fake = faker.Faker()


@pytest.fixture(scope='function', autouse=False)
def url():
    return reverse('chat:index')


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
async def test_send_message_without_setup(url, client):
    user = baker.make(models.USER_MODEL)
    client.force_login(user)
    request = client.get(url).wsgi_request

    communicator = WebsocketCommunicator(ChatConsumer, url)
    communicator.scope['session'] = request.session

    chat = baker.make(models.CHAT_MODEL)
    data = {
        'type': 'send_message',
        'chat': chat.pk,
        'message': fake.word(),
    }
    await communicator.send_json_to(data)
    response = await communicator.receive_json_from()

    assert 'error' in response

    # Disconnect
    await communicator.disconnect()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_send_message(url, client):
    user = baker.make(models.USER_MODEL)
    client.force_login(user)
    request = client.get(url).wsgi_request
    session = request.session

    communicator = WebsocketCommunicator(ChatConsumer, url)
    communicator.scope['session'] = session

    chat = baker.make(models.CHAT_MODEL)
    # Setup
    data = {
        'type': 'setup_channel_layer',
        'chat': chat.pk,
        'session_key': session.session_key,
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
    message = response['message']

    assert word == message['message']
    assert chat.pk == message['chat']

    assert ChatMessage.objects.get(pk=message['id'])

    # Disconnect
    await communicator.disconnect()
