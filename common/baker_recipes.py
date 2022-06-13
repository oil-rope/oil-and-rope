from django.apps import apps
from model_bakery.recipe import Recipe, foreign_key

from common.constants import models
from common.utils import create_faker
from registration.baker_recipes import user

fake = create_faker()

ContentType = apps.get_model(models.CONTENT_TYPE)
Vote = apps.get_model(models.COMMON_VOTE)

vote = Recipe(
    Vote,
    user=foreign_key(user),
    is_positive=fake.pybool,
)

campaign_vote = vote.extend(
    content_type=ContentType.objects.get(app_label='roleplay', model='campaign'),
)

place_vote = vote.extend(
    content_type=ContentType.objects.get(app_label='roleplay', model='place'),
)
