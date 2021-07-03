from django.apps import apps
from model_bakery.recipe import Recipe, related

from common.constants import models
from common.utils import create_faker
from registration.baker_recipes import user

fake = create_faker()

Chat = apps.get_model(models.CHAT_MODEL)

chat = Recipe(
    Chat,
    name=fake.sentence,
    users=related(user),
)
