from unittest.mock import MagicMock, patch

from django.test import TestCase
from model_bakery import baker

from chat import models
from tests.mocks.discord import channel_response
from tests.utils import fake


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

    @patch('bot.utils.discord_api_request')
    def test_discord_chat_is_returned_when_discord_id_given_ok(self, mocker_api_request: MagicMock):
        discord_id = f'{fake.random_number(digits=18)}'
        mocker_api_request.return_value = channel_response(id=discord_id)
        instance = baker.make_recipe('chat.chat', discord_id=discord_id)

        self.assertIsNotNone(instance.discord_chat)


class TestChatMessage(TestCase):
    model = models.ChatMessage

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(cls.model)

    def test_str_ok(self):
        expected = f'{self.instance.message} ({self.instance.entry_created_at})'

        self.assertEqual(expected, str(self.instance))
