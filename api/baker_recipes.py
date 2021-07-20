from model_bakery.recipe import Recipe, foreign_key
from rest_framework.authtoken.models import Token

from common.utils import create_faker
from registration.baker_recipes import user

fake = create_faker()

token = Recipe(
    Token,
    user=foreign_key(user),
)
