import pathlib

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from bot.exceptions import OilAndRopeException


def load_env_file(env_file: pathlib.Path):
    """
    Looks for the given .env file and sets up Environment Variables.
    """

    if not isinstance(env_file, pathlib.Path):
        env_file = pathlib.Path(str(env_file))

    if not env_file.exists():
        raise OilAndRopeException(_('Env file does not exist') + '.')
    load_dotenv(env_file.as_posix(), verbose=True, override=True)
