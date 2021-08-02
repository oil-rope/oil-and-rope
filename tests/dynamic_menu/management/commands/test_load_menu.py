import json
import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from faker import Faker

from dynamic_menu.enums import MenuTypes
from dynamic_menu.models import DynamicMenu


class TestLoadMenuCommand(TestCase):

    def setUp(self):
        self.tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', dir='./tests/', delete=False)
        self.data = [
            {
                'name': 'First Menu',
                'name_en_us': 'First Menu',
                'name_es_ES': 'Primer Menú',
                'menu_type': MenuTypes.MAIN_MENU,
                'children': [{
                        'name': 'First Submenu',
                        'name_en_us': 'First Submenu',
                        'name_es_ES': 'Primer Submenú',
                        'menu_type': MenuTypes.MAIN_MENU,
                        'children': [{
                            'name': 'First Context Menu',
                            'name_en_us': 'First Context Menu',
                            'name_es_ES': 'Primer Menú Contextual',
                            'menu_type': MenuTypes.CONTEXT_MENU
                        }]
                }]
            },
            {
                'name': 'Second Menu',
                'name_en_us': 'Second Menu',
                'name_es_ES': 'Segundo Menú',
                'menu_type': MenuTypes.MAIN_MENU,
            }
        ]

        self.json_file = self.tmp_file.name
        with open(self.json_file, 'w') as f:
            json.dump(self.data, f)
        self.faker = Faker()

    def tearDown(self):
        # Cleaning
        self.tmp_file.close()
        os.unlink(self.tmp_file.name)

    def test_syntax_ok(self):
        out = StringIO()
        json_file = self.json_file
        call_command('load_menu', json_file, stdout=out)
        msg = 'Menu initialized.'
        # Since it returns colors we better just get if our message is in the final output
        self.assertIn(msg, out.getvalue())

    def test_load_data_ok(self):
        call_command('load_menu', self.json_file)

        entries = DynamicMenu.objects.count()
        expected_len = 4
        self.assertEqual(expected_len, entries, 'Menu entries were not correctly created.')

    def test_load_non_existent_file_ko(self):
        json_file = self.faker.file_name(category='text', extension='json')
        with self.assertRaises(CommandError) as ex:
            call_command('load_menu', json_file)
        exception = ex.exception
        msg = 'Fixture does not exist.'
        self.assertEqual(msg, str(exception))

    def test_load_non_file_ko(self):
        tempdir = tempfile.TemporaryDirectory(dir='./tests/')
        json_file = tempdir.name
        with self.assertRaises(CommandError) as ex:
            call_command('load_menu', json_file)
        exception = ex.exception
        msg = 'Fixture is not a file.'
        self.assertEqual(msg, str(exception))

    def test_syntax_ko(self):
        with self.assertRaises(CommandError) as ex:
            call_command('load_menu')
        msg_regex = r'.*arguments are required: fixture.*'
        exception = ex.exception
        self.assertRegex(str(exception), msg_regex)
