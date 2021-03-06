import asyncio
import logging
import os
import pathlib
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import errors
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from faker import Faker

from bot.categories import MiscellaneousCog, RoleplayCog, UserCog

from . import utils
from .exceptions import HelpfulError, OilAndRopeException

LOGGER = logging.getLogger(__name__)
fake = Faker()  # To generate tokens and stuff


class OilAndRopeBot(commands.Bot):
    """
    Custom class to control the behaviour of the bot by environment variables.
    """

    def __init__(self, env_file=None, **options):
        if env_file:
            self.load_env_file(env_file)
        self.load_variables()
        super().__init__(command_prefix=self.command_prefix, description=self.description, **options)

        # Manually registering events
        # TODO: Search if there's a better way to do this
        self.event(self.on_guild_join)

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

        if not isinstance(env_file, pathlib.Path):
            env_file = pathlib.Path(str(env_file))

        if not env_file.exists():
            raise OilAndRopeException(_('Env file does not exist') + '.')
        load_dotenv(env_file.as_posix(), verbose=True, override=True)

    def load_commands(self):
        """
        Reads all the commands from `bot.commands` and adds them to the bot command list.
        """

        print('\nLoading commands ', end='')

        # List of categories
        cogs = [MiscellaneousCog, RoleplayCog, UserCog]
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

        name = 'awesome sessions!'
        name += f'Type \'{settings.BOT_COMMAND_PREFIX}help\' for help.'
        activity = discord.Game(name=name)
        status = discord.Status.online
        await self.change_presence(activity=activity, status=status)

    async def on_guild_join(self, guild):
        owner = guild.owner
        # Say hello in System's messages channel or first in list
        greet_channel = guild.system_channel or guild.text_channels[0]
        async with greet_channel.typing():
            msg = 'Hello! You are about to experience a brand-new way to manage sessions and play!'
            msg += f'\nStart by typing `{settings.BOT_COMMAND_PREFIX}invite`.'
            await greet_channel.send(f'{msg}')
        await utils.get_or_create_discord_user(owner)
        await utils.get_or_create_discord_server(guild)

    async def on_message(self, message: discord.Message):
        if not message.author.bot and message.content.startswith(self.command_prefix):
            author = message.author.name
            author_id = message.author.id
            message_content = message.content
            log_message = f'{author} ({author_id}): {message_content}'
            print(log_message)
        await super().on_message(message)

    async def on_command_error(self, context, exception):
        if isinstance(exception, errors.MissingRequiredArgument):
            await context.send(_('Incorrect format') + '.')
            await context.send_help(context.command)

    def run(self, *args, **kwargs):
        self.load_commands()
        super().run(self.token, *args, **kwargs)

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
        msg = _('Hello traveller! To confirm your account please type %(token)s') % {'token': '`{}`'.format(token)}
        await user.send(msg)

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
            await user.send(_('Token has timed out' + '!'))
        else:
            await utils.get_or_create_discord_user(user)
            await user.send(_('Your user has been confirmed') + '!')
