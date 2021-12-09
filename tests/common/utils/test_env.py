import platform
import shutil
import tempfile
import unittest

from django.test import TestCase

from common.utils.env import load_env_file
from common.utils.faker import create_faker

fake = create_faker()


class TestEnv(TestCase):
    def test_load_env_with_all_expected_values_ok(self):
        # NOTE: Windows doesn't have writting permission on %AppData%\Temp
        env_file = tempfile.NamedTemporaryFile(dir='./tests/')
        env_file.close()
        # We basically copy .env.example file
        shutil.copy('.env.example', env_file.name)
        # Then we load environment variables
        load_env_file(env_file.name)

    @unittest.skipIf(
        condition=lambda: platform.system() == 'Windows',
        reason='Windows system doesn\'t properly work with tempfile'
    )
    def test_load_env_without_expected_values_ko(self):
        env_file = tempfile.NamedTemporaryFile(dir='./tests/')
        env_file.close()
        with self.assertRaisesRegex(Warning, r'Some values are missing from .+'):
            load_env_file(env_file.name)

    def test_load_env_non_existent_file_ko(self):
        env_file = fake.file_path()
        with self.assertRaisesRegex(ImportError, r'File .+ couldn\'t be found'):
            load_env_file(env_file)
