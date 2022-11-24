import functools
import random

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone as tz
from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key

from registration.baker_recipes import user
from tests.utils import english_faker, fake, generate_place, spanish_faker

from .enums import DomainTypes, RoleplaySystems, SiteTypes
from .models import Campaign, Domain, Place, Race, Session, Trait, TraitType

random_date_after_today = functools.partial(
    fake.date_time_between, tzinfo=tz.get_current_timezone(), start_date='now', end_date='+1y'
)
random_domain_type = functools.partial(random.choice, DomainTypes.values)
random_roleplay_system = functools.partial(random.choice, RoleplaySystems.values)
random_site_type = functools.partial(random.choice, SiteTypes.values)

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
    strength=lambda: fake.random_int(min=-5, max=5),
    dexterity=lambda: fake.random_int(min=-5, max=5),
    constitution=lambda: fake.random_int(min=-5, max=5),
    intelligence=lambda: fake.random_int(min=-5, max=5),
    wisdom=fake.random_int(min=-5, max=5),
    charisma=lambda: fake.random_int(min=-5, max=5),
    affected_by_armor=fake.pybool,
    owner=foreign_key('registration.user'),
    campaign=foreign_key('roleplay.campaign'),
    place=generate_place,
)

race_without_modifiers = race.extend(
    strength=0,
    dexterity=0,
    constitution=0,
    intelligence=0,
    wisdom=0,
    charisma=0,
)

race_for_campaign_only = race.extend(
    place=None,
)

race_for_place_only = race.extend(
    campaign=None,
)

race_without_optional = race.extend(
    name='',
    description='',
    campaign=None,
    place=None,
)

trait_type = Recipe(
    TraitType,
    name=english_faker.sentence(nb_words=3),
    name_es=spanish_faker.sentence(nb_words=3),
    description=english_faker.sentence(),
    description_es=spanish_faker.sentence(),
)

trait = Recipe(
    Trait,
    name=fake.sentence(nb_words=3),
    description=fake.sentence(),
    type=foreign_key('roleplay.trait_type'),
    content_type=lambda: ContentType.objects.get_for_model(Race),
    object_id=lambda: baker.make_recipe('roleplay.race').id,
)
