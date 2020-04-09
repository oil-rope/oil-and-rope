import os
import tempfile
from unittest.mock import patch

import dotenv
from django.test import TestCase
from faker import Faker

from bot.bot import OilAndRopeBot
from bot.exceptions import HelpfulError


class TestOilAndRopeBot(TestCase):
    """
    Checks beahviour of the bot.
    """

    def setUp(self):
        self.faker = Faker()
        self.bot_class = OilAndRopeBot
        self.env_variables = {
            'BOT_COMMAND_PREFIX': self.faker.word(),
            'BOT_TOKEN': self.faker.password()
        }

    @classmethod
    def setUpClass(cls):
        # Creating temporary file
        cls.env_file = tempfile.NamedTemporaryFile(mode='w', suffix='.env', dir='./tests/', delete=False)

    @classmethod
    def tearDownClass(cls):
        # Cleaning
        cls.env_file.close()
        os.unlink(cls.env_file.name)

    def test_init_ok(self):
        with patch.dict('os.environ', self.env_variables):
            bot = self.bot_class()
            self.assertEqual(self.env_variables['BOT_COMMAND_PREFIX'], bot.command_prefix)
            self.assertEqual(self.env_variables['BOT_TOKEN'], bot.token)

    def test_init_with_env_file_ok(self):
        # Creating temporary file
        env_file = self.env_file.name

        # Make sure .env file is created
        self.assertTrue(dotenv.load_dotenv(env_file), '.env file is not loaded.')
        # Adds text
        dotenv.set_key(env_file, 'BOT_COMMAND_PREFIX', self.env_variables['BOT_COMMAND_PREFIX'])
        dotenv.set_key(env_file, 'BOT_TOKEN', self.env_variables['BOT_TOKEN'])

        with patch.dict('os.environ'):
            bot = self.bot_class(env_file=env_file)
            self.assertEqual(self.env_variables['BOT_COMMAND_PREFIX'], bot.command_prefix)
            self.assertEqual(self.env_variables['BOT_TOKEN'], bot.token)

    def test_instance_without_bot_token_ko(self):
        msg = 'Use .env file or set up BOT_TOKEN environment variables.'
        key = 'BOT_COMMAND_PREFIX'
        with patch.dict('os.environ', {key: self.env_variables[key]}):
            with self.assertRaises(HelpfulError) as ex:
                self.bot_class()
        self.assertIn(msg, str(ex.exception))

    def test_instance_without_command_prefix_ko(self):
        msg = 'Use .env file or set up BOT_COMMAND_PREFIX environment variables.'
        key = 'BOT_TOKEN'
        with patch.dict('os.environ', {key: self.env_variables[key]}):
            with self.assertRaises(HelpfulError) as ex:
                self.bot_class()
        self.assertIn(msg, str(ex.exception))
