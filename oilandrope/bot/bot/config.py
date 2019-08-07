import configparser
import logging
import pathlib
import shutil

from django.utils.translation import ugettext as _

from bot.bot.exceptions import OilAndRopeException

LOG = logging.getLogger(__name__)
CONFIG_DIR = pathlib.Path('bot/config/')
EXAMPLE_CONFIG_DIR = 'example_configuration.ini'
CONFIG_FILE = 'configuration.ini'


class Config:
    """
    Handles configuration from `config/configuration.ini`.
    """

    def __init__(self):
        self.configuration = self.get_configuration()

    def get_configuration(self) -> configparser.ConfigParser:
        """
        Checks if config file exists and returns its ConfigParser.
        """

        example_config = CONFIG_DIR / EXAMPLE_CONFIG_DIR

        # Checks if example configuration file was moved or removed
        if not example_config.exists():
            LOG.error(_("File '%(example_config)s' not found!\nDid you removed it?" % {'example_config': example_config}))
            raise OilAndRopeException(_("Example Config file is needed in order to start the bot."))

        config_file = CONFIG_DIR / CONFIG_FILE

        # Checks if configuration file doesn't exists
        if not config_file.exists():
            try:
                example_config = str(example_config.absolute())
                config_file = str(config_file.absolute())
                shutil.copy(example_config, config_file)
            except IOError:
                LOG.error(_("Couldn't copy configuration file!\nDo you have read and write permissions?"))
                OilAndRopeException(_("You need permissions to copy the configuration file."))

        # Creating the parser
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(config_file, encoding='utf-8')

        return parser
