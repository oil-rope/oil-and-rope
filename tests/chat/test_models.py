from django.test import TestCase
from model_bakery import baker

from chat import models


class TestChat(TestCase):
    model = models.Chat

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(cls.model)

    def test_str_ok(self):
        expected = f'{self.instance.name} ({self.instance.pk})'

        self.assertEqual(expected, str(self.instance))


class TestChatMessage(TestCase):
    model = models.ChatMessage

    @classmethod
    def setUpTestData(cls):
        cls.instance = baker.make(cls.model)

    def test_str_ok(self):
        expected = f'{self.instance.message} ({self.instance.entry_created_at})'

        self.assertEqual(expected, str(self.instance))
