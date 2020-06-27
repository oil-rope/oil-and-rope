from django.shortcuts import reverse
from django.test import TestCase, override_settings
from faker.proxy import Faker

from bot.discord_api.models import Channel, Message

from .helpers.constants import LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER


@override_settings(
    DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN,
    ALLOWED_HOSTS=['*', 'testserver']
)
class TestSendMessageToDiscordUserView(TestCase):

    def setUp(self):
        self.discord_user = USER_WITH_SAME_SERVER
        self.faker = Faker()
        self.data = {
            'discord_user_id': self.discord_user,
            'message_content': self.faker.word(),
        }
        self.url = reverse('bot:utils:send_message')

    def test_post_ok(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(201, response.status_code)

    def test_post_missing_data_ko(self):
        response = self.client.post(self.url, data={})

        self.assertEqual(400, response.status_code)

    @override_settings(ALLOWED_HOSTS=['localhost', 'testserver', '127.0.0.1'])
    def test_post_from_outer_ko(self):
        response = self.client.post(self.url, data=self.data, REMOTE_ADDR=self.faker.ipv4())

        self.assertEqual(403, response.status_code)

    @override_settings(ALLOWED_HOSTS=['develop.oilandrope-project.com', 'testserver'])
    def test_post_from_outer_ok(self):
        response = self.client.post(self.url, data=self.data, HTTP_ORIGIN='http://develop.oilandrope-project.com')

        self.assertEqual(201, response.status_code)

    def test_post_msg_created_ok(self):
        response = self.client.post(self.url, data=self.data)
        channel = Channel(response.json()['channel_id'])
        msg = Message(channel, response.json()['id'])

        self.assertEqual(response.json(), msg.json_response)


@override_settings(
    DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN,
    ALLOWED_HOSTS=['*', 'testserver']
)
class TestSendInvitationView(TestCase):

    def setUp(self):
        self.discord_user = USER_WITH_SAME_SERVER
        self.data = {
            'discord_user_id': self.discord_user
        }
        self.url = reverse('bot:utils:send_invitation')

    def test_post_ok(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(201, response.status_code)

    def test_post_missing_data_ko(self):
        response = self.client.post(self.url, data={})

        self.assertEqual(400, response.status_code)
