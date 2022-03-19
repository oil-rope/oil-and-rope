from django.test import TestCase, override_settings
from model_bakery import baker

from chat import models
from tests.bot.helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN


class TestChat(TestCase):
    model = models.Chat

    def setUp(self):
        self.instance = baker.make(self.model)

    def test_str_ok(self):
        expected = f'{self.instance.name} ({self.instance.pk})'

        self.assertEqual(expected, str(self.instance))

    def test_discord_chat_without_discord_id(self):
        self.assertIsNone(self.instance.discord_chat)

    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_discord_chat_with_discord_id(self):
        self.instance.discord_id = CHANNEL

        self.assertIsNotNone(self.instance.discord_chat)


class TestChatMessage(TestCase):
    model = models.ChatMessage

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(cls.model)

    def test_str_ok(self):
        expected = f'{self.instance.message} ({self.instance.entry_created_at})'

        self.assertEqual(expected, str(self.instance))
