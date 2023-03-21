import logging
import os
import pathlib
from typing import Optional, Union

from dotenv import dotenv_values, load_dotenv

LOGGER = logging.getLogger(__name__)


def check_env_file(env_file: pathlib.Path) -> None:
    """
    Checks that all values in .env.example are in .env file.
    """

    project_dir = pathlib.Path(__file__).resolve().parent.parent.parent
    example_env_file = project_dir / '.env.example'

    if not example_env_file.is_file() or not example_env_file.exists():  # pragma: no cover
        raise Warning(f'File \'{example_env_file}\' couldn\'t be found')

    env_keys = dotenv_values(env_file)
    expected_keys = dotenv_values(example_env_file)
    missing_keys = []

    for key in expected_keys:
        if key not in env_keys:
            missing_keys.append(key)

    if missing_keys:
        missing_values = ', '.join(missing_keys)
        raise Warning(f'Some values are missing from \'{env_file}\': {missing_values}')


def load_env_file(env_file: Union[pathlib.Path, str]) -> bool:
    """
    Looks for the given .env file and sets up Environment Variables.

    Parameters
    ----------
    env_file: :class:`Union[pathlib.Path, str]`
        The dotenv file from which to load environment variables.

    Returns
    -------
    Same value as :method:`dotenv.load_dotenv`.
    """

    if isinstance(env_file, str):
        env_file = pathlib.Path(env_file)

    if not env_file.is_file() or not env_file.exists():
        LOGGER.warning('File \'%s\' couldn\'t be found. Using environment variables', str(env_file))
        return False

    check_env_file(env_file)
    return load_dotenv(env_file, override=False, verbose=True, encoding='utf-8')


def load_secrets(
    secret_env_variables: list[str] = [
        'SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'EMAIL_HOST', 'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD', 'BOT_TOKEN',
    ],
    extra_env_variables: list[str] = [],
    encoding: Optional[str] = None
):
    """
    Looks for specific environment variables and check if they are files. If this is true it will read the file value
    and set it as the environment variable.

    Parameters
    ----------
    secret_env_variables: :class:`list[str]`
        List of environment variables to iterate and check for files.
    extra_env_variables: :class:`list[str]`
        Any extra environment variable to check besides the given ones in `secret_env_variables`.
    encoding: :class:`Optional[str]`
        Encoding used for reading the files.
    """

    env_variables = secret_env_variables + extra_env_variables
    for env_var in env_variables:
        if env_var not in os.environ:
            continue
        file = pathlib.Path(os.environ[env_var])
        if file.exists() and file.is_file():
            os.environ[env_var] = file.read_text(encoding=encoding)
