import unittest

from django.test import TestCase, override_settings
from model_bakery import baker

from chat import models
from tests.utils import check_litecord_connection

from ..bot.helpers.constants import CHANNEL, LITECORD_API_URL, LITECORD_TOKEN


class TestChat(TestCase):
    model = models.Chat

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make_recipe('chat.chat')

    def test_str_ok(self):
        expected = f'{self.instance.name} ({self.instance.pk})'

        self.assertEqual(expected, str(self.instance))

    def test_discord_chat_is_not_reached_when_no_discord_id(self):
        self.assertIsNone(self.instance.discord_chat)

    @unittest.skipIf(not check_litecord_connection(), 'Litecord seems to be unreachable.')
    @override_settings(DISCORD_API_URL=LITECORD_API_URL, BOT_TOKEN=LITECORD_TOKEN)
    def test_discord_chat_is_returned_when_discord_id_given_ok(self):
        instance = baker.make_recipe('chat.chat', discord_id=CHANNEL)

        self.assertIsNotNone(instance.discord_chat)


class TestChatMessage(TestCase):
    model = models.ChatMessage

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(cls.model)

    def test_str_ok(self):
        expected = f'{self.instance.message} ({self.instance.entry_created_at})'

        self.assertEqual(expected, str(self.instance))
