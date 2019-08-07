import pytest

from django.test import TestCase

from bot.bot import config


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

    def test_creates_config_file(self):
        """
        Validates that config file was created.
        """

        config_file = config.CONFIG_DIR / config.CONFIG_FILE
        self.assertTrue(config_file.exists())
