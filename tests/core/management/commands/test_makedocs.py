from unittest.mock import MagicMock, patch

from django.core.management import CommandError, call_command
from django.test import TestCase


class TestCommand(TestCase):
    command_name = 'makedocs'

    def test_syntax_without_app_label_ko(self):
        with self.assertRaisesRegex(CommandError, r'Error: Enter at least one application label\.'):
            call_command(self.command_name)

    def test_non_existent_app_label_ko(self):
        app_label = 'random'
        with self.assertRaisesRegex(CommandError, r'No installed app with label \'.+\'.*'):
            call_command(self.command_name, app_label)

    @patch('core.management.commands.makedocs.main')
    def test_syntax_with_excludes_ok(self, mocker: MagicMock):
        call_command(self.command_name, 'common', exclude=['**/migrations', 'random', 'excellent'])

        mocker.assert_called_once()
        self.assertIn('**/migrations', mocker.call_args[0][0])
