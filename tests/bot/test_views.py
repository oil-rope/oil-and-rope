from django.shortcuts import reverse
from django.test import TestCase, override_settings

from .helpers.constants import LITECORD_API_URL, LITECORD_TOKEN, USER_WITH_SAME_SERVER
from faker.proxy import Faker
from bot.discord_api.models import Channel, Message


@override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
class TestSendMessageToDiscordUserView(TestCase):

    def setUp(self):
        self.discord_user = USER_WITH_SAME_SERVER
        self.faker = Faker()
        self.data = {
            'message_content': self.faker.word()
        }
        self.url = reverse('bot:utils:send_message', kwargs={'discord_user': self.discord_user})

    def test_post_ok(self):
        response = self.client.post(self.url, data=self.data)

        self.assertEqual(201, response.status_code)

    def test_post_missing_data_ko(self):
        response = self.client.post(self.url, data={})

        self.assertEqual(400, response.status_code)

    def test_post_msg_created_ok(self):
        response = self.client.post(self.url, data=self.data)
        channel = Channel(response.json()['channel_id'])
        msg = Message(channel, response.json()['id'])

        self.assertEqual(response.json(), msg.json_response)
