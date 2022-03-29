import functools
import random

from django.apps import apps
from django.utils import timezone as tz
from model_bakery.recipe import Recipe, foreign_key, related

from chat.baker_recipes import chat
from common.constants import models
from common.utils import create_faker
from registration.baker_recipes import user

from .enums import DomainTypes, RoleplaySystems, SiteTypes

fake = create_faker()
random_date_after_today = functools.partial(
    fake.date_time_between, tzinfo=tz.get_current_timezone(), start_date='now', end_date='+1y'
)
random_domain_type = functools.partial(random.choice, DomainTypes.values)
random_roleplay_system = functools.partial(random.choice, RoleplaySystems.values)
random_site_type = functools.partial(random.choice, SiteTypes.values)

Domain = apps.get_model(models.DOMAIN_MODEL)
Place = apps.get_model(models.PLACE_MODEL)
Session = apps.get_model(models.SESSION_MODEL)

place = Recipe(
    Place,
    name=fake.country,
    description=fake.paragraph,
    site_type=random_site_type,
    owner=foreign_key(user),
)

world = Recipe(
    Place,
    name=fake.country,
    description=fake.paragraph,
    site_type=SiteTypes.WORLD,
    owner=foreign_key(user),
)

domain = Recipe(
    Domain,
    name=fake.word,
    description=fake.paragraph,
    domain_type=random_domain_type,
)

session = Recipe(
    Session,
    name=fake.sentence,
    plot=fake.paragraph,
    players=related(user),
    chat=foreign_key(chat),
    next_game=random_date_after_today,
    system=random_roleplay_system,
    world=foreign_key(world),
)
