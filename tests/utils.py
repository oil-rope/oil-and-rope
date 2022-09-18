import logging
import random
from typing import TYPE_CHECKING, Union
from unittest import mock

from model_bakery import baker

from common.utils.faker import create_faker
from roleplay.enums import SiteTypes

if TYPE_CHECKING:
    from roleplay.models import Place

LOGGER = logging.getLogger(__name__)

fake = create_faker()


def generate_place(_quantity=1, **kwargs) -> Union[list['Place'], 'Place']:
    """
    Generates a list of Place objects with given kwargs.

    Parameters
    ----------
    _quantity: Optional[:class:`int`]
        Number of places to generate.
    """

    import roleplay.models

    places: list['Place'] = []
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
