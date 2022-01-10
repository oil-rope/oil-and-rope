from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase


class TestCommand(TestCase):
    command_name = 'compiledocs'

    @patch('core.management.commands.compiledocs.main')
    def test_syntax_with_excludes_ok(self, mocker: MagicMock):
        call_command(self.command_name)

        mocker.assert_called_once()
