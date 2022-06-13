import functools
import random

from django.apps import apps
from django.utils import timezone as tz
from model_bakery.recipe import Recipe, foreign_key

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

Campaign = apps.get_model(models.ROLEPLAY_CAMPAIGN)
Domain = apps.get_model(models.ROLEPLAY_DOMAIN)
Place = apps.get_model(models.ROLEPLAY_PLACE)
Session = apps.get_model(models.ROLEPLAY_SESSION)
Race = apps.get_model(models.ROLEPLAY_RACE)

place = Recipe(
    Place,
    name=fake.country,
    description=fake.paragraph,
    site_type=random_site_type,
    owner=foreign_key(user),
)

world = place.extend(
    site_type=SiteTypes.WORLD,
)

private_world = world.extend(
    user=foreign_key(user),
)

domain = Recipe(
    Domain,
    name=fake.word,
    description=fake.paragraph,
    domain_type=random_domain_type,
)

campaign = Recipe(
    Campaign,
    name=functools.partial(fake.sentence, nb_words=3),
    system=random_roleplay_system,
    is_public=fake.pybool,
)

public_campaign = campaign.extend(
    is_public=True,
)

private_campaign = campaign.extend(
    is_public=False,
)

session = Recipe(
    Session,
    name=fake.sentence,
    description=fake.paragraph,
    plot=fake.words,
    gm_info=fake.paragraph,
    next_game=random_date_after_today,
)

race = Recipe(
    Race,
    name=fake.word(),
    description=fake.paragraph(),
    strength=fake.random_int(min=-5, max=5),
    dexterity=fake.random_int(min=-5, max=5),
    charisma=fake.random_int(min=-5, max=5),
    constitution=fake.random_int(min=-5, max=5),
    intelligence=fake.random_int(min=-5, max=5),
    affected_by_armor=True,
    wisdom=fake.random_int(min=-5, max=5),
    image=fake.image_url(),
)

race_without_optional = race.extend(
    description='',
    image='',
    affected_by_armor=False,
)
