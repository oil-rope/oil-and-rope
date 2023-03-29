
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from model_bakery.recipe import Recipe, foreign_key

from common.models import Image, Vote
from common.utils import create_faker
from registration.baker_recipes import user

fake = create_faker()

image = Recipe(
    Image,
    image=f'{settings.MEDIA_ROOT}/{fake.file_path(category="image", absolute=False)}',
    owner=foreign_key(user),
)

race_image = image.extend(
    content_type=ContentType.objects.get(app_label='roleplay', model='race'),
)

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
