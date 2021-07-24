import logging
import os
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import errors
from django.conf import settings
from django.utils.translation import gettext as _
from faker import Faker

from common.utils.env import load_env_file

from .exceptions import HelpfulError

LOGGER = logging.getLogger(__name__)
fake = Faker()  # To generate tokens and stuff


class OilAndRopeBot(commands.Bot):
    """
    Custom class to control the behaviour of the bot by environment variables.
    """

    def __init__(self, env_file=None, **options):
        self.command_prefix = None
        self.description = None
        self.token = None
        if env_file:
            load_env_file(env_file)
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

    def load_commands(self):
        """
        Reads all the commands from `bot.commands` and adds them to the bot command list.
        """

        print('\nLoading commands ', end='')

        # List of categories
        cogs = []
        new_commands = []

        for cog in cogs:
            cog = cog()
            self.add_cog(cog)
            new_commands.extend(cog.get_commands())
            [print('.', end='') for _ in new_commands]

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

    async def first_join_message(self, channel):
        greetings_msg = _('hello!').capitalize()
        info_msg = _('you are about to experience a brand-new way to manage sessions and play!').capitalize()
        msg = f'{greetings_msg} {info_msg}'
        await channel.send(f'{msg}')

    async def on_guild_join(self, guild):
        # Say hello in System's messages channel or first in list
        greet_channel = guild.system_channel or guild.text_channels[0]
        async with greet_channel.typing():
            await self.first_join_message(greet_channel)

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
