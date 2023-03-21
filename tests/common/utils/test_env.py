import os
import pathlib
import shutil
import tempfile
from unittest import mock

from django.test import TestCase

from common.utils.env import load_env_file, load_secrets
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
        # NOTE: Windows doesn't have writing permission on %AppData%\Temp
        env_file = self.tmp_file
        # We basically copy .env.example file
        shutil.copy('.env.example', str(env_file))
        # Then we load environment variables
        load_env_file(str(env_file))

    def test_load_env_without_expected_values_ko(self):
        env_file = self.tmp_file
        with self.assertRaisesRegex(Warning, r'Some values are missing from .+'):
            load_env_file(str(env_file))

    @mock.patch('common.utils.env.LOGGER')
    def test_load_env_non_existent_file_raises_warning_ok(self, logger_mock: mock.MagicMock):
        load_env_file(fake.file_name(extension='env'))

        logger_mock.warning.assert_called_once_with(
            'File \'%s\' couldn\'t be found. Using environment variables',
            mock.ANY,
        )

    @mock.patch.dict('os.environ')
    def test_load_secrets_all_are_files_ok(self):
        secret_env_variables = [
            'SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'EMAIL_HOST', 'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD', 'BOT_TOKEN',
        ]

        for env_var in secret_env_variables:
            secret_value: str = fake.pystr()
            env_file = tempfile.NamedTemporaryFile(prefix=f'{env_var}-')
            with open(env_file.name, 'w') as file_obj:
                file_obj.write(secret_value)
            os.environ[env_var] = env_file.name

        load_secrets()

        for env_var in secret_env_variables:
            assert env_var in os.environ

            assert not pathlib.Path(os.environ[env_var]).is_file()
            assert isinstance(os.environ[env_var], str)

    @mock.patch.dict('os.environ')
    def test_load_secrets_only_certain_values_ok(self):
        secret_key: str = fake.pystr()
        secret_key_file = tempfile.NamedTemporaryFile(prefix='SECRET_KEY-')
        with open(secret_key_file.name, 'w') as file_obj:
            file_obj.write(secret_key)
        os.environ['SECRET_KEY'] = secret_key_file.name

        db_password: str = fake.pystr()
        db_password_file = tempfile.NamedTemporaryFile(prefix='DB_PASSWORD-')
        with open(db_password_file.name, 'w') as file_obj:
            file_obj.write(db_password)
        os.environ['DB_PASSWORD'] = db_password_file.name

        load_secrets()

        assert os.environ['SECRET_KEY'] == secret_key
        assert os.environ['DB_PASSWORD'] == db_password

    @mock.patch.dict('os.environ')
    def test_load_secrets_with_non_existent_values_in_environment_variables_ok(self):
        load_secrets(secret_env_variables=['RANDOM_VALUE'])

        assert 'RANDOM_VALUE' not in os.environ
