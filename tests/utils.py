import requests

from tests.bot.helpers.constants import LITECORD_API_URL


def check_litecord_connection() -> bool:
    """
    Simple function to check if Litecord is working.
    """

    response = requests.get(url=LITECORD_API_URL, timeout=5)
    return response.ok
