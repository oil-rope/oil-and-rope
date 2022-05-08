import random

from django.apps.registry import apps

from common.constants import models
from common.utils.faker import create_faker
from roleplay.enums import SiteTypes

fake = create_faker()

Place = apps.get_model(models.ROLEPLAY_PLACE)


def bake_places(_quantity=None, user=None, owner=None):
    """
    This function is a quick fix since MpttModel doesn't work well with baker.
    """

    if not _quantity:
        _quantity = fake.pyint(min_value=1, max_value=10)
    places = []
    for _ in range(0, _quantity):
        places.append(Place.objects.create(
            name=fake.country(),
            description=fake.paragraph(),
            site_type=random.choice(SiteTypes.values),
            user=user,
            owner=owner,
        ))
    return places[0] if len(places) == 1 else places
