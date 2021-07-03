import functools
import random

from django.apps import apps
from model_bakery.recipe import Recipe, foreign_key, related

from common.constants import models
from common.utils import create_faker
from registration.baker_recipes import user

from .enums import RoleplaySystems, SiteTypes

fake = create_faker()
random_roleplay_system = functools.partial(random.choice, RoleplaySystems.values)
random_date_after_today = functools.partial(fake.date_this_year, before_today=False, after_today=True)

Place = apps.get_model(models.PLACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)

world = Recipe(
    Place,
    name=fake.country,
    description=fake.paragraph,
    site_type=SiteTypes.WORLD,
    owner=foreign_key(user),
)

session = Recipe(
    Session,
    name=fake.sentence,
    description=fake.paragraph,
    players=related(user),
    next_game=random_date_after_today,
    system=random_roleplay_system,
    world=foreign_key(world),
)
