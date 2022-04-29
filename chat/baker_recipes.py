from django.apps import apps
from model_bakery.recipe import Recipe, foreign_key, related

from common.constants import models
from common.utils import create_faker
from registration.baker_recipes import user

fake = create_faker()

Chat = apps.get_model(models.CHAT)
ChatMessage = apps.get_model(models.CHAT_MESSAGE)

chat = Recipe(
    Chat,
    name=fake.word,
    users=related(user),
)

message = Recipe(
    ChatMessage,
    chat=foreign_key(chat),
    message=fake.sentence,
    author=foreign_key(user),
)
