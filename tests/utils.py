import logging
import random
from typing import List

import requests
from model_bakery import baker

import roleplay.models
from roleplay.enums import SiteTypes
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


def generate_place(_quantity=1, **kwargs) -> List[roleplay.models.Place]:
    """
    Generates a list of Place objects with given kwargs.
    """

    places = []
    for _ in range(0, _quantity):
        user = baker.make_recipe('registration.user')
        params = {
            'name': fake.country(),
            'description': fake.text(),
            'site_type': random.choice(SiteTypes.values),
            'user': user,
            'owner': user,
        }
        params.update(kwargs)
        # NOTE: Bulk create does **not** work with `mptt`
        places += [roleplay.models.Place.objects.create(**params)]

    return places if len(places) > 1 else places[0]
