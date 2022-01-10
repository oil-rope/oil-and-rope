import pathlib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from sphinx.cmd.build import main


class Command(BaseCommand):
    help = 'Creates documentation with Sphinx.'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            'builder',
            nargs='?',
            help='The builder to use. For more information about builders run with "help" as builder.',
            default='html',
            type=str,
        )

    def handle(self, *args, **options):
        docs_dir = pathlib.Path(settings.BASE_DIR) / 'docs'
        build_dir = docs_dir / '_build'
        builder = options['builder']
        # NOTE: First argument is "builder", second "sourcedir" and third "outputdir"
        main(['-M', builder, str(docs_dir), build_dir])
