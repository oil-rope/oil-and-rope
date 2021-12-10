import pathlib
import shutil
import tempfile

from django.test import TestCase

from common.utils.env import load_env_file
from common.utils.faker import create_faker

fake = create_faker()


class TestEnv(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_file = pathlib.Path(self.tmp_dir) / fake.file_name(extension='env')
        self.tmp_file.touch()

    def tearDown(self):
        self.tmp_file.unlink()
        pathlib.Path(self.tmp_dir).rmdir()

    def test_load_env_with_all_expected_values_ok(self):
        # NOTE: Windows doesn't have writting permission on %AppData%\Temp
        env_file = self.tmp_file
        # We basically copy .env.example file
        shutil.copy('.env.example', str(env_file))
        # Then we load environment variables
        load_env_file(str(env_file))

    def test_load_env_without_expected_values_ko(self):
        env_file = self.tmp_file
        with self.assertRaisesRegex(Warning, r'Some values are missing from .+'):
            load_env_file(str(env_file))

    def test_load_env_non_existent_file_ko(self):
        env_file = fake.file_path()
        with self.assertRaisesRegex(ImportError, r'File .+ couldn\'t be found'):
            load_env_file(env_file)
