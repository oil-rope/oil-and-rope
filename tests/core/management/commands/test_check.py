from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class TestCheckCommand(TestCase):

    def test_call_command_ok(self):
        out = StringIO()
        call_command('check', stdout=out)
        msg = 'System check identified no issues (0 silenced).\n'
        self.assertEqual(
            msg,
            out.getvalue(),
            'Seems like you have check issues.\nPlease run \'python manage.py check\''
        )
