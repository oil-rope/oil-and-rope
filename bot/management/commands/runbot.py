import os
import pathlib

from discord.ext import commands
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.utils.translation import ugettext_lazy as _
from dotenv import load_dotenv

from bot import OilAndRopeBot


class Command(BaseCommand):

    help = _('Runs Discord Bot')

    def setup(self, env_file=None):
        self.bot = OilAndRopeBot(env_file=env_file)
        self.bot.run()

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--env', nargs='?', type=str, required=False, help=_('Custom .env file to read.'))

    def handle(self, *args, **options):
        env_file = options['env']

        try:
            # Looking for .env
            if env_file:
                env_file = pathlib.Path(env_file)
            # Start the bot
            self.setup(env_file)
        except CommandError as ex:
            message_error = '{error}'.format(error=ex)
            self.stdout.write(self.style.ERROR(message_error))
