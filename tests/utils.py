import logging

import requests

from tests.bot.helpers.constants import LITECORD_API_URL

LOGGER = logging.getLogger(__name__)


def check_litecord_connection() -> bool:
    """
    Simple function to check if Litecord is working.
    """

    try:
        response = requests.get(url=LITECORD_API_URL, timeout=5)
        return response.ok
    except requests.exceptions.ConnectionError as ex:
        LOGGER.exception(ex)
        return False
