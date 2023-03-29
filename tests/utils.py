import logging
import random
from typing import TYPE_CHECKING
from unittest import mock

from model_bakery import baker

from common.utils.faker import create_faker
from roleplay.enums import SiteTypes

if TYPE_CHECKING:
    from registration.models import User
    from roleplay.models import Place

LOGGER = logging.getLogger(__name__)

fake = create_faker()
english_faker = create_faker(locales=['en'])
spanish_faker = create_faker(locales=['es'])


def generate_place(_quantity=1, **kwargs):
    """
    Generates a list of Place objects with given kwargs.

    Parameters
    ----------
    _quantity: Optional[:class:`int`]
        Number of places to generate.
    """

    import roleplay.models

    places: list['Place'] = []
    owner: 'User' = kwargs.get('owner')
    for _ in range(0, _quantity):
        owner: 'User' = baker.make_recipe('registration.user') if not owner else owner
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
