"""
Oil & Rope
~~~~~~~~~~

A bot connected to Oil & Rope web to make Roleplay Games more interactive.
"""

import asyncio
import logging
import os
import pathlib
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import errors
from django.utils.translation import ugettext_lazy as _
from dotenv import load_dotenv
from faker import Faker

from bot.categories import MiscellaneousCog, RoleplayCog

from . import utils
from .exceptions import HelpfulError, OilAndRopeException

LOGGER = logging.getLogger(__name__)
fake = Faker()  # To generate tokens and stuff


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

        # List of categories
        cogs = [MiscellaneousCog, RoleplayCog]
        commands = []

        for cog in cogs:
            cog = cog()
            self.add_cog(cog)
            commands.extend(cog.get_commands())
            [print('.', end='') for c in commands]

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
        if not message.author.bot and message.content.startswith(self.command_prefix):
            log_message = '{author} ({id}): {message}'.format(
                author=message.author.name,
                id=message.author.id,
                message=message.content
            )
            print(log_message)
        await super(OilAndRopeBot, self).on_message(message)

    async def on_command_error(self, context, exception):
        if isinstance(exception, errors.MissingRequiredArgument):
            await context.send('Incorrect format.')
            await context.send_help(context.command)

    def run(self, *args, **kwargs):
        super(OilAndRopeBot, self).run(self.token, *args, **kwargs)

    async def confirm_user(self, user_id):
        """
        Gets given ID and DMs user for confirming identity.

        Parameters
        ----------
        user_id: :class:`int`
            The user to confirm.
        """

        user = self.get_user(user_id)
        token = fake.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True)
        await user.send('Hello traveller! To confirm your account please type `{token}`'.format(token=token))

        def check(m):
            """
            This check looks for token in message and user.
            """

            token_confirm = m.content == token
            user_confirm = m.author == user
            return token_confirm and user_confirm

        try:
            await self.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await user.send('Token has timed out!')
        else:
            await user.send('Your user has been confirmed!')
            utils.get_or_create_discord_user(user)
