import logging
import random
from typing import List, Union
from unittest import mock

import requests
from model_bakery import baker

import roleplay.models
from roleplay.enums import SiteTypes
from roleplay.models import Place
from tests.bot.helpers.constants import LITECORD_API_URL, LITECORD_TOKEN

from . import fake

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


def generate_place(_quantity: int = 1, **kwargs) -> Union[List[Place], Place]:
    """
    Generates a list of Place objects with given kwargs.

    Parameters
    ----------
    _quantity: Optional[:class:`int`]
        Number of places to generate.
    """

    places: List[Place] = []
    owner = kwargs.get('owner')
    for _ in range(0, _quantity):
        owner = baker.make_recipe('registration.user') if not owner else owner
        params = {
            'name': fake.country(),
            'description': fake.text(),
            'site_type': random.choice(SiteTypes.values),
            'owner': owner,
        }
        params.update(kwargs)
        # NOTE: Bulk create does **not** work with `mptt`
        places += [roleplay.models.Place.objects.create(**params)]

    return places if _quantity > 1 else places[0]


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
