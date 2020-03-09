import configparser
import logging
import os
import pathlib
import shutil

from .exceptions import OilAndRopeException

LOG = logging.getLogger(__name__)
CONFIG_DIR = pathlib.Path(__file__).parent / 'config/'
EXAMPLE_CONFIG_DIR = 'example_configuration.ini'
CONFIG_FILE = 'configuration.ini'
CONF_SECTIONS = {'Credentials', 'Bot', 'Embed'}  # Obligatory sections


class Config:
    """
    Handles configuration from `config/configuration.ini`.
    """

    def __init__(self):
        self.config_file = self.get_configuration()
        self.configuration = {section: {} for section in self.config_file.sections()}

        for section in self.config_file.sections():
            for option in self.config_file[section]:
                # Getting the value
                value = self.config_file.get(section, option)
                self.configuration[section].update({option: value})

        # Checking for sensitive crendentials
        if 'token' not in self.configuration['Credentials']:
            LOG.warning("\nToken not found in 'Credentials'\nLooking in environment variables 'BOT_TOKEN'\n")
            self.configuration['Credentials'].update({'token': os.getenv('BOT_TOKEN', '')})

    def get_configuration(self) -> configparser.ConfigParser:
        """
        Checks if config file exists and returns its ConfigParser.
        """

        example_config = CONFIG_DIR / EXAMPLE_CONFIG_DIR

        # Checks if example configuration file was moved or removed
        if not example_config.exists():
            LOG.error("File '%(example_config)s' not found!\nDid you removed it?", {'example_config': example_config})
            raise OilAndRopeException("Example Config file is needed in order to start the bot.")

        config_file = CONFIG_DIR / CONFIG_FILE

        # Checks if configuration file doesn't exists
        if not config_file.exists():
            try:
                shutil.copy(str(example_config), str(config_file))
            except IOError:
                LOG.error("Couldn't copy configuration file!\nDo you have read and write permissions?")
                OilAndRopeException("You need permissions to copy the configuration file.")

        # Creating the parser
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(str(config_file), encoding='utf-8')

        missing_sections = CONF_SECTIONS.difference(parser.sections())
        if missing_sections:
            raise OilAndRopeException(
                "There are missing sections: %(sections)s" % {'sections': ', '.join(missing_sections)}
            )

        return parser
