import pathlib

from django import apps
from django.conf import settings
from django.core.management.base import AppCommand, CommandParser
from sphinx.ext.apidoc import main


class Command(AppCommand):
    help = 'Generates ReStructuredText documentation (.rst) for Sphinx from given App.'

    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)
        parser.add_argument(
            '--exclude',
            help='Pattern to exclude from making docs.',
            nargs='?',
            action='append',
            type=str,
        )

    def handle_app_config(self, app_config: apps.AppConfig, **options):
        docs_dir = pathlib.Path(settings.BASE_DIR) / 'docs'
        excludes = options['exclude']
        if not excludes:
            excludes = ['**/migrations', '**/apps.py', '**/urls.py', '**/admin.py']
        main(['-o', str(docs_dir), app_config.path, *excludes])
