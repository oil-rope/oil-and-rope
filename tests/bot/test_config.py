import pathlib

import pytest
from django.test import TestCase

from bot import config, exceptions


@pytest.fixture(scope='module', autouse=True)
def del_config_file():
    """
    Deletes config file and unnecesary files after test.
    """

    yield

    config_file = config.CONFIG_DIR / config.CONFIG_FILE
    config_file.unlink()


class ConfigFileTest(TestCase):
    """
    Checks if config file is created, read and applied correctly.
    """

    def setUp(self):
        self.config_file = config.CONFIG_DIR / config.CONFIG_FILE

    def test_creates_config_file(self):
        """
        Validates that config file was created.
        """

        self.assertTrue(self.config_file.exists(), 'Config file does not exist.')

    def test_config_file_ko(self):
        """
        Checks if invalid config file raises exception.
        """

        self.config_file = pathlib.Path(__file__).parent / 'files/configuration.ini'

        with self.assertRaises(exceptions.OilAndRopeException):
            self.assertTrue(self.config_file.exists(), 'Config file does not exist.')
            config_parser = config.Config(config_file=self.config_file)
