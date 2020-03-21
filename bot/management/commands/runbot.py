import os
import pathlib

from discord.ext import commands
from django.core.management.base import (BaseCommand, CommandError,
                                         CommandParser)
from django.utils.translation import ugettext_lazy as _
from dotenv import load_dotenv


class Command(BaseCommand):

    help = _('Runs Discord Bot')

    def setup(self):
        command_prefix = os.getenv('BOT_COMMAND_PREFIX', '..')
        description = os.getenv('BOT_DESCRIPTION', '')
        token = os.getenv('BOT_TOKEN')
        self.bot = commands.Bot(command_prefix=command_prefix, description=description)

        self.load_commands()
        self.bot.run(token)

    def load_commands(self):
        """
        Reads all the commands from `bot.commands` and adds them to the bot command list.
        """

        from bot.commands import logout

        commands = [logout]

        for command in commands:
            self.bot.add_command(command)

    def load_env_file(self, env_file: pathlib.Path):
        """
        Looks for the given .env file and sets up Environment Variables.
        """

        if not env_file.exists():
            raise CommandError(_('Env file doesn\'t exist.'))
        load_dotenv(env_file.as_posix())

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--env', nargs='?', type=str, required=False, help=_('Custom .env file to read.'))

    def handle(self, *args, **options):
        env_file = options['env']

        try:
            # Looking for .env
            if env_file:
                env_file = pathlib.Path(env_file)
                self.load_env_file(env_file)
            # Start the bot
            self.setup()
        except CommandError as ex:
            message_error = '{error}'.format(error=ex)
            self.stdout.write(self.style.ERROR(message_error))
