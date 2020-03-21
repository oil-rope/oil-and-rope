"""
Oil & Rope
~~~~~~~~~~

A bot connected to Oil & Rope web to make Roleplay Games more interactive.
"""

import logging
import os
import pathlib
from datetime import datetime

import discord
from discord.ext import commands
from django.utils.translation import ugettext_lazy as _
from dotenv import load_dotenv

from .exceptions import OilAndRopeException, HelpfulError

LOGGER = logging.getLogger(__name__)


class OilAndRopeBot(commands.Bot):
    """
    Custom class to control the behaviour of the bot by enviroment variables.
    """

    def __init__(self, env_file=None, **options):
        if env_file:
            self.load_env_file(env_file)
        self.load_variables()
        super(OilAndRopeBot, self).__init__(command_prefix=self.command_prefix, description=self.description, **options)
        self.load_commands()

    def load_variables(self):
        """
        Loads required variables for the bot.
        """

        try:
            self.command_prefix = os.environ['BOT_COMMAND_PREFIX']
            self.description = os.getenv('BOT_DESCRIPTION', '')
            self.token = os.environ['BOT_TOKEN']
        except KeyError as ex:
            missing_variables = ', '.join(ex.args)
            error_message = 'Environment variables %s not found.' % missing_variables
            solution = 'Use .env file or set up %s environment variables.' % missing_variables
            raise HelpfulError(error_message, solution, preface='Error loading bot variables.')

    def load_env_file(self, env_file: pathlib.Path):
        """
        Looks for the given .env file and sets up Environment Variables.
        """

        if not env_file.exists():
            raise OilAndRopeException(_('Env file doesn\'t exist.'))
        load_dotenv(env_file.as_posix())

    def load_commands(self):
        """
        Reads all the commands from `bot.commands` and adds them to the bot command list.
        """

        print('\nLoading commands ', end='')

        from bot.commands import logout

        commands = [logout]
        commands_to_load = [c.name for c in commands]
        LOGGER.info('Commands to load: %s', ', '.join(commands_to_load))

        for command in commands:
            self.add_command(command)
            print('.', end='')

        # Linebreak to clean up
        print('\n')

    async def on_ready(self):
        init_message = '{bot} is ready!\nID: {id}\nAt {time}'.format(
            bot=self.user.name,
            id=self.user.id,
            time=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
        LOGGER.info(init_message)
        print(init_message)

    async def on_message(self, message: discord.Message):
        log_message = '{author} ({id}): {message}'.format(
            author=message.author.name,
            id=message.author.id,
            message=message.content
        )
        print(log_message)
        await super(OilAndRopeBot, self).on_message(message)

    def run(self, *args, **kwargs):
        super(OilAndRopeBot, self).run(self.token, *args, **kwargs)
