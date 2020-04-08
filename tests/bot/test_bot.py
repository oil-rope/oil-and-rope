from django.test import TestCase

from bot.bot import OilAndRopeBot
from bot.exceptions import HelpfulError


class TestOilAndRopeBot(TestCase):
    """
    Checks beahviour of the bot.
    """

    def setUp(self):
        self.bot_class = OilAndRopeBot

    def test_instance_without_command_prefix(self):
        msg = 'Use .env file or set up BOT_COMMAND_PREFIX environment variables.'
        with self.assertRaises(HelpfulError) as ex:
            self.bot_class()
            self.assertIn(msg, ex.message)
