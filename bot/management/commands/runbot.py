from django.core.management.base import BaseCommand

from bot import OilAndRopeBot


class Command(BaseCommand):

    help = 'Runs Discord Bot.'

    def setup(self):
        self.bot = OilAndRopeBot()
        self.bot.run()

    def handle(self, *args, **options):
        # Start the bot
        self.setup()
