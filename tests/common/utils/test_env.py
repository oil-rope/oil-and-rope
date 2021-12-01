import shutil
import tempfile

from django.test import TestCase

from common.utils.env import load_env_file
from common.utils.faker import create_faker

fake = create_faker()


class TestEnv(TestCase):
    def test_load_env_with_all_expected_values_ok(self):
        with tempfile.NamedTemporaryFile(mode='w') as env_file:
            # We basically copy .env.example file
            shutil.copy('.env.example', env_file.name)
            # Then we load environment variables
            load_env_file(env_file.name)

    def test_load_env_without_expected_values_ko(self):
        with tempfile.NamedTemporaryFile(mode='r') as env_file:
            with self.assertRaisesRegex(Warning, r'Some values are missing from .+'):
                load_env_file(env_file.name)

    def test_load_env_non_existent_file_ko(self):
        env_file = fake.file_path()
        with self.assertRaisesRegex(ImportError, r'File .+ couldn\'t be found'):
            load_env_file(env_file)
