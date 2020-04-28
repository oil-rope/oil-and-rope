from django.test import TestCase

from bot.models import DiscordServer, DiscordTextChannel, DiscordUser, DiscordVoiceChannel
from model_bakery import baker


class TestDiscordServer(TestCase):

    def setUp(self):
        self.instance = baker.make(DiscordServer)

    def test_str_ok(self):
        expected = 'Server {} ({})'.format(self.instance.name, self.instance.pk)
        self.assertEqual(expected, str(self.instance))


class TestDiscordTextChannel(TestCase):

    def setUp(self):
        self.instance = baker.make(DiscordTextChannel)

    def test_str_ok(self):
        expected = 'Text Channel {} ({})'.format(self.instance.name, self.instance.pk)
        self.assertEqual(expected, str(self.instance))


class TestDiscordUser(TestCase):

    def setUp(self):
        self.instance = baker.make(DiscordUser)

    def test_str_ok(self):
        expected = '{}#{}'.format(self.instance.nick, self.instance.code)
        self.assertEqual(expected, str(self.instance))


class TestDiscordVoiceChannel(TestCase):

    def setUp(self):
        self.instance = baker.make(DiscordVoiceChannel)

    def test_str_ok(self):
        expected = self.instance.name
        self.assertEqual(expected, str(self.instance))
