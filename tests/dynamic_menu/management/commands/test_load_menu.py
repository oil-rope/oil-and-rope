import json
import os
import pathlib
import tempfile
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from faker import Faker

from dynamic_menu.models import DynamicMenu


class TestLoadMenuCommand(TestCase):

    def setUp(self):
        self.data = [
            {
                'name': 'First Menu',
                'name_en': 'First Menu',
                'name_es': 'Primer Menú',
                'menu_type': DynamicMenu.MAIN_MENU,
                'children': [{
                        'name': 'First Submenu',
                        'name_en': 'First Submenu',
                        'name_es': 'Primer Submenú',
                        'menu_type': DynamicMenu.MAIN_MENU,
                        'children': [{
                            'name': 'First Context Menu',
                            'name_en': 'First Context Menu',
                            'name_es': 'Primer Menú Contextual',
                            'menu_type': DynamicMenu.CONTEXT_MENU
                        }]
                }]
            },
            {
                'name': 'Second Menu',
                'name_en': 'Second Menu',
                'name_es': 'Segundo Menú',
                'menu_type': DynamicMenu.MAIN_MENU,
            }
        ]
        self.faker = Faker()

    @classmethod
    def setUpClass(cls):
        cls.json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', dir='./tests/', delete=False)

    @classmethod
    def tearDownClass(cls):
        # Cleaning
        cls.json_file.close()
        os.unlink(cls.json_file.name)

    def test_syntax_ok(self):
        out = StringIO()
        json_file = self.json_file.name
        call_command('load_menu', json_file, stdout=out)
        msg = 'Menu initialized.\n'
        self.assertEqual(msg, out.getvalue())

    def test_load_data_ok(self):
        json_data = json.dumps(self.data)
        json_file = self.json_file.name
        json_file = pathlib.Path(json_file)
        json_file.write_text(json_data)

        call_command('load_menu', str(json_file))

        entries = DynamicMenu.objects.count()
        expected_len = 4
        self.assertEqual(expected_len, entries, 'Menu entries weren\'t correctly created.')

    def test_load_inexistent_file_ko(self):
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
