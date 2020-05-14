import pathlib

from django.test import TestCase

from bot import config, exceptions


class ConfigFileTest(TestCase):
    """
    Checks if config file is created, read and applied correctly.
    """

    def setUp(self):
        self.config = config.Config()
        self.config_file = self.config.config_file

    def tearDown(self):
        self.config_file.unlink()

    def test_creates_config_file(self):
        """
        Validates that config file was created.
        """

        self.assertTrue(self.config_file.exists(), 'Config file does not exist.')

    def test_config_file_ko(self):
        """
        Checks if invalid config file raises exception.
        """

        config_file = pathlib.Path('./configuration.ini')
        config_file.touch()

        with self.assertRaises(exceptions.OilAndRopeException):
            self.assertTrue(config_file.exists(), 'Config file does not exist.')
            config.Config(config_file=config_file)

        config_file.unlink()
