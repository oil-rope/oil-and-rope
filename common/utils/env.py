import logging
import pathlib
from typing import Union

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
    """

    if isinstance(env_file, str):
        env_file = pathlib.Path(env_file)

    if not env_file.is_file() or not env_file.exists():
        LOGGER.warning('File \'%s\' couldn\'t be found. Using environment variables', str(env_file))
        return False

    check_env_file(env_file)
    return load_dotenv(env_file, override=False, verbose=True, encoding='utf-8')
