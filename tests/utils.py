import logging

import requests

from tests.bot.helpers.constants import LITECORD_API_URL, LITECORD_TOKEN

LOGGER = logging.getLogger(__name__)


def check_litecord_connection() -> bool:
    """
    Simple function to check if Litecord is working.
    """

    try:
        # NOTE: Since API Info seems to be dropped we check on bot user
        response = requests.get(
            url=f'{LITECORD_API_URL}users/@me',
            timeout=5,
            headers={
                'Authorization': f'Bot {LITECORD_TOKEN}',
            }
        )
        return response.ok
    except requests.exceptions.ConnectionError as ex:
        LOGGER.exception(ex)
        return False
