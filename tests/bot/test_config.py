import pathlib

from django.test import TestCase

import pytest
from bot import config, exceptions


@pytest.fixture(scope='class')
def del_config_file(request):
    """
    Deletes config file and unnecesary files after test.
    """

    request.cls.config = config.Config()
    request.cls.config_file = config.CONFIG_DIR / config.CONFIG_FILE

    yield

    request.cls.config_file.unlink()


@pytest.mark.usefixtures('del_config_file')
class ConfigFileTest(TestCase):
    """
    Checks if config file is created, read and applied correctly.
    """

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
            config.Config(config_file=self.config_file)
