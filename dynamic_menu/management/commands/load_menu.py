import json
import pathlib

from django.core.management.base import (BaseCommand, CommandError,
                                         CommandParser)

from dynamic_menu import models, utils


class Command(BaseCommand):
    """
    This command will initialize the menu from a JSON file.
    """

    help = 'Initialize the menu from a JSON file.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('fixture', help='JSON file with data.',
                            nargs=1, type=str)

    def handle(self, *args, **options):
        # Reading arguments and parsing
        if 'fixture' in options:
            json_file = pathlib.Path(options.get('fixture', '')[0])
        else:
            json_file = pathlib.Path('')

        if not json_file.exists():
            raise CommandError('Fixture does not exist.')
        if not json_file.is_file():
            raise CommandError('Fixture is not a file.')

        # Reading JSON
        data = json.load(json_file.open())
        # Creating entries
        utils.populate(data, models.DynamicMenu)

        self.stdout.write(self.style.SUCCESS('Menu initialized.'))
