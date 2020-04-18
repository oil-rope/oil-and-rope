from django.test import TestCase
from faker import Faker

from bot.exceptions import OilAndRopeException
from bot.models import DiscordServer, DiscordTextChannel, DiscordUser
from bot.utils import get_or_create_discord_server, get_or_create_discord_text_channel, get_or_create_discord_user

from .helpers import mocks


class TestBotUtils(TestCase):

    def setUp(self):
        self.faker = Faker()
        self.member = mocks.MemberMock()
        self.guild = mocks.GuildMock()
        self.text_channel = mocks.TextChannelMock()

    def test_get_or_create_discord_user_ok(self):
        # Unexistent member
        self.assertFalse(DiscordUser.objects.exists())
        entry = get_or_create_discord_user(self.member)
        self.assertEqual(1, DiscordUser.objects.count())
        self.assertEqual(str(self.member.id), str(entry.id))

        # Existent member
        entry = get_or_create_discord_user(self.member)
        self.assertEqual(1, DiscordUser.objects.count())
        self.assertEqual(str(self.member.id), str(entry.id))

    def test_get_or_create_discord_user_without_member_ko(self):
        # Unexistent member
        self.assertFalse(DiscordUser.objects.exists())
        with self.assertRaises(OilAndRopeException) as ex:
            get_or_create_discord_user(None)
        exception_msg = 'Discord User cannot be None.'
        self.assertEqual(exception_msg, str(ex.exception))

    def test_get_or_create_discord_server_ok(self):
        # First we need to create the owner
        get_or_create_discord_user(self.guild.owner)

        # Unexistent sever
        self.assertFalse(DiscordServer.objects.exists())
        entry = get_or_create_discord_server(self.guild)
        self.assertEqual(1, DiscordServer.objects.count())
        self.assertEqual(str(self.guild.id), str(entry.id))

        # Existent sever
        entry = get_or_create_discord_server(self.guild)
        self.assertEqual(1, DiscordServer.objects.count())
        self.assertEqual(str(self.guild.id), str(entry.id))

    def test_get_or_create_discord_text_channel(self):
        # First we need to create the server
        get_or_create_discord_server(self.text_channel.guild)
        # Then we need to create the owner
        get_or_create_discord_user(self.text_channel.guild.owner)

        # Unexistent text channel
        self.assertFalse(DiscordTextChannel.objects.exists())
        entry = get_or_create_discord_text_channel(self.text_channel, self.text_channel.guild)
        self.assertEqual(1, DiscordTextChannel.objects.count())
        self.assertEqual(str(self.text_channel.id), str(entry.id))

        # Existent text channel
        entry = get_or_create_discord_text_channel(self.text_channel, self.text_channel.guild)
        self.assertEqual(1, DiscordTextChannel.objects.count())
        self.assertEqual(str(self.text_channel.id), str(entry.id))
